import cv2
import torch
from django.http import StreamingHttpResponse
from lpapp.function import utils_rotate
from lpapp.function import helper
from django.views.decorators import gzip
from .models import *
import random
import base64
import numpy as np
import io
import time  
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse


yolo_LP_detect = torch.hub.load('yolov5', 'custom', path=r'M:\lpproject\lpapp\model\LP_detector.pt', force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path=r'M:\lpproject\lpapp\model\LP_ocr.pt', force_reload=True, source='local')
yolo_license_plate.conf = 0.60

def process_frame(frame):
    plates = yolo_LP_detect(frame, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()
    captured_image_path = None  # Initialize captured image path

    if len(list_plates) > 0:
        plate = list_plates[0]  # Assuming you want to process the first license plate found
        x, y, w, h = map(int, plate[:4])
        crop_img = frame[y:y + h, x:x + w]
        
        # Save cropped license plate image
        captured_image_path = "media/processed_images/captured_crop.jpg"
        cv2.imwrite(captured_image_path, crop_img)

        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp)
                    cv2.putText(frame, lp, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    break

    # Save processed frame image
    captured_image_path_full = "media/processed_images/captured_image.jpg"
    cv2.imwrite(captured_image_path_full, frame)

    # Return the captured image path and license plate number
    return captured_image_path_full, captured_image_path, lp





def capture_and_process(request):
    lp = LicensePlate.objects.all()
    lp.delete()
    if request.method == 'POST' and 'image_data' in request.POST:
        # Decode base64 image data
        image_data = request.POST['image_data'].split(',')[1]
        image_bytes = io.BytesIO(base64.b64decode(image_data))

        # Convert image bytes to numpy array
        image_np = np.frombuffer(image_bytes.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if frame is not None:
            # Process the frame and get captured image path and license plate number
            captured_image_path_full, captured_image_path, lp_number = process_frame(frame)

            # Check if the license plate number is already associated with an active parking transaction
            existing_transactions = ParkingTransaction.objects.filter(vehicle=lp_number, exit_time=None)

            if existing_transactions.exists():
                # If multiple active transactions are found, choose the latest one
                existing_transaction = existing_transactions.latest('entry_time')
                # Parking transaction already exists, save exit time and redirect to end_parking_transaction
                existing_transaction.exit_time = timezone.now()
                existing_transaction.save()

                existing_transaction.parking_slot.is_available = True
                existing_transaction.parking_slot.lp_number = None 
                existing_transaction.parking_slot.save()
                
                return redirect('end_parking_transaction', lpnum=lp_number)
            else:
                # No existing transaction found, allot a parking slot for the new license plate number
                if lp_number:
                    # Get a free parking slot
                    free_slot = ParkingSlot.objects.filter(is_available=True).first()

                    if free_slot:
                        # Start a parking transaction
                        entry_time = timezone.now()
                        ParkingTransaction.objects.create(vehicle=lp_number, parking_slot=free_slot, entry_time=entry_time)
                        free_slot.is_available = False  # Mark the slot as occupied
                        free_slot.lp_number = lp_number 
                        free_slot.save()

                        # Calculate time elapsed since entry
                        time_elapsed = timezone.now() - entry_time

                        # Render the result template with the required information
                        return render(request, 'result.html', {'captured_image_path': captured_image_path_full,
                                                                'parking_slot': free_slot.slot_number,
                                                                'entry_time': entry_time,
                                                                'time_elapsed': time_elapsed})

            # Return the path to the processed image for display
            return render(request, 'result.html', {'captured_image_path': captured_image_path_full,
                                                    'error_message': 'No free slot available.'})

    # Return an error message if image processing fails
    return render(request, 'result.html', {'error_message': 'Failed to process image.'})



def index(request):
    parking_slot = ParkingSlot.objects.all()
    
    return render(request, 'index.html',{'parking_slots': parking_slot})

def base(request):
    return render(request, 'base.html')

def result(request):
    return render(request, 'result.html')



def parking_slots(request):
    parking_slot = ParkingSlot.objects.all()
    lpno=LicensePlate.objects.all()
    return render(request, 'slot.html', {'parking_slots': parking_slot,'lpno':lpno})

 
def start_parking_transaction(request,slot_number):
     if 'lpnum' in request.GET:
        lp_number = request.GET['lpnum']

        ParkingTransaction.objects.create(
            vehicle=lp_number,
            parking_slot=slot_number
        )

        return render(request,'block.html',{'lp_number':lp_number,'slot_number':slot_number})
    

def end_parking_transaction(request, lpnum):
    # Get the latest parking transaction for the given license plate number
    parking_transaction = ParkingTransaction.objects.filter(vehicle=lpnum).latest('entry_time')

    # Calculate the duration of the stay
    duration = parking_transaction.exit_time - parking_transaction.entry_time

    if duration.total_seconds() <= 3600:
        price=40
    elif duration.total_seconds() > 3600:
        price=60
    elif duration.total_seconds() > 7200:
        price=80
    elif duration.total_seconds() > 10800:
        price=100
    elif duration.total_seconds() > 14400:
        price=120
    elif duration.total_seconds() > 18000:
        price=140
    elif duration.total_seconds() > 21600:
        price=160
    
     
    # Render a template with the parking details and the calculated price
    return render(request, 'end_parking.html', {'parking_transaction': parking_transaction, 'price': price})

def payment(request):
    price=request.GET.get('price')
    vehicle=request.GET.get('vehicle')
    return render(request,'payment.html',{'price':price,'vehicle':vehicle })

def get_parking_slots(request):
    # Query the database to get parking slot data
    parking_slots = ParkingSlot.objects.all()

    # Serialize parking slot data to JSON format
    slots_data = [
        {
            "slot_number": slot.slot_number,
            "is_available": slot.is_available,
            "lp_number": slot.lp_number if slot.lp_number else ""  # Include lp_number or an empty string if it's None
        }
        for slot in parking_slots
    ]

    # Return JSON response
    return JsonResponse(slots_data, safe=False)




def generate_transaction_id():
    # Generate a random 14-digit transaction ID
    return ''.join([str(random.randint(0, 9)) for _ in range(14)])

def transaction_receipt(request):
    vehicle_number = request.GET.get('vehicle', '')
    price = request.GET.get('price', '')

    # Retrieve all parking transactions for the given vehicle number
    parking_transactions = ParkingTransaction.objects.filter(vehicle=vehicle_number).order_by('-entry_time')

    if parking_transactions.exists():
        # Get the most recent parking transaction
        parking_transaction = parking_transactions[0]

        # Extract necessary details from the parking transaction
        transaction_id = generate_transaction_id()
        vehicle = parking_transaction.vehicle
        parking_slot = parking_transaction.parking_slot.slot_number
        entry_time = parking_transaction.entry_time
        exit_time = parking_transaction.exit_time
        priceof = price # Assuming you have a function to calculate the price

        # Save the transaction data to the database (optional)
        Transaction.objects.create(
            transaction_id=transaction_id,
            vehicle=vehicle,
            parking_slot=parking_slot,
            entry_time=entry_time,
            exit_time=exit_time,
            price=priceof
        )

        # Pass the data to the receipt template
        context = {
            'transaction_id': transaction_id,
            'vehicle': vehicle,
            'parking_slot': parking_slot,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'price': price
        }

        return render(request, 'receipt.html', context)
  


