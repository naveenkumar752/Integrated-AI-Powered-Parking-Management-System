
from django.db import models

class LicensePlate(models.Model):
    plate_number = models.CharField(max_length=50, unique=True)
    plate_image = models.ImageField(upload_to='license_plate_images/', blank=True, null=True)

    def __str__(self):
        return self.plate_number
    

class ParkingSlot(models.Model):
    slot_number = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)
    lp_number = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return self.slot_number    
    



class ParkingTransaction(models.Model):
    vehicle = models.CharField(max_length=200)
    parking_slot = models.ForeignKey(ParkingSlot,on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.parking_slot} - Entry: {self.entry_time} - Exit: {self.exit_time}"




class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    vehicle = models.CharField(max_length=200)
    parking_slot = models.CharField(max_length=100)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Transaction ID: {self.transaction_id}, Vehicle: {self.vehicle}, Parking Slot: {self.parking_slot}"
