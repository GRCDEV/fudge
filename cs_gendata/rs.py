import string    
import random # define the random module  

S = 10  # number of characters in the string.  

ran = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = S))    

print("The randomly generated string is : " + ran) # print the random data  