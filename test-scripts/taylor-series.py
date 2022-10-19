import zlib
import math

def factorial(num):  
    f = 1    
    if num < 0:    
       print(" Factorial does not exist for negative numbers")
       return 1
    elif num == 0:    
       print("The factorial of 0 is 1")
       return 1
    else:    
       for i in range(1,num + 1):    
           f = f*i
       return f 

secret = "hello-world"
encoded_secret = secret.encode()
byte_array = bytearray(encoded_secret)

# hash secret message
output = hex(zlib.crc32(encoded_secret) & 0xffffffff)

print(byte_array)
print(str(output[2:]))


P0=-44
d0= 1
n=2.5
Pr=-60


x = math.log(10, math.e) * ((P0-Pr)/(10*n))

# Taylor series
taylor_s = 1
L = 6
for i in range(1, L+1):
    taylor_s += pow(x,i) / factorial(i)

d = d0 * taylor_s
print("Distance calculated using taylor series is " + str(d))

#Distance between the Transmitter and Receiver
d1 = d0 * pow(10, ((P0-Pr)/(10*n)))
print("Calculated distance using log formula is " + str(d1))



