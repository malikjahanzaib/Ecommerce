from django.db import models
#for using our auth user model
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES =(
    #'what goes in db' ,'what is displayed'
    ('S','Shirt'),
    ('SW','Sports wear'),
    ('OW','Outwear')
)

LABEL_CHOICES =(
    #'what goes in db' ,'what is displayed'
    ('p','primary'),
    ('S','secondary'),
    ('D','danger')
)

''' 
LIFE CYCLE OF A ORDER IN ECOMMERCE
1. Item added to cart
2. Adding a billing address
(failed checkout)
3.Payment service
(preprocessing,processing,packaging)
4.Being Delievred/ready to deliver
5.Received
6.Refunds
'''

# Create your models here.

#inherits models class defined in django
#Model for the items we can purchase
#but when you add a item to the cart it becomes Orderitem
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    #diff imgs for diff items
    image = models.ImageField()
    discount_price = models.FloatField(blank=True, null =True)
    category = models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label = models.CharField(choices=LABEL_CHOICES,max_length=1)
    slug =models.SlugField()
    description = models.TextField()
   
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product",kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",kwargs={
            'slug': self.slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",kwargs={
            'slug': self.slug
        })
    
   
    



#this model is used to link between item model and the order model
class OrderItem(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    ordered =models.BooleanField(default=False)
    #for making a one to many relation between Item model and Orderitem model
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
     #default is one so that when a product is added to cart only one instance of that is added to cart
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
   
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    
   

#model for shopping cart in which you add a product to order
class Order(models.Model):
    #for associating a order with a user
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    #reference code  is used for reffering to a order when asked for a refund
    ref_code = models.CharField(max_length=20)
   #items for adding orderitems into order
    items = models.ManyToManyField(OrderItem)
   #for storing the time the order was *created*
    start_date =models.DateTimeField(auto_now_add=True)
   #storing manually here that value the moment that the item is ordered
    ordered_date = models.DateTimeField()
    #when a product is ordered
    ordered = models.BooleanField(default=False)

    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL ,blank=True, null=True)
    #as we want to get the payment Model related to the order itself as we did with billing address
    payment = models.ForeignKey('Payment',on_delete=models.SET_NULL ,blank=True, null=True)

    #we want here to assign the coupon to the order
    coupon = models.ForeignKey('Coupon',on_delete=models.SET_NULL ,blank=True, null=True)

    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False) 
    refund_requested = models.BooleanField(default=False) ##imp field which needs some work
    refund_granted = models.BooleanField(default=False) 
   
    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        #subtract amount of coupon applied from total here
        if self.coupon:
            total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
     user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

     street_address = models.CharField(max_length=100)
     house_address = models.CharField(max_length=100)
     country =CountryField(multiple=False)
     zip = models.CharField(max_length=100)

     def __str__(self):
        return self.user.username


#as we want to keep track of actual stripe payment thus we create a class for it
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    #if the user is deleted we dont want the payment to be deleted as we want to keep track of every payment
    #thus we keep the user field on_delete as null
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.SET_NULL, blank=True ,null =True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code =models.CharField(max_length=15)
    #amount that is to subtracted from total when coupon is applied
    amount = models.FloatField()

    def __str__(self):
        return self.code

#to store the refund for our own use
class Refund(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    #reason for refunding the order
    reason = models.TextField()
    #if refund accepted or not
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        #pk=primary key
        return f"{self.pk}"







#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<self parameter >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#The self parameter is a reference to the current instance of the class, and is used to access variables that belongs to the class.
# #It does not have to be named self , you can call it whatever you like, but it has to be the first parameter of any function in the class: