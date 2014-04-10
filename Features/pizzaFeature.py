import random

class pizzaFeature:

    def __init__(self):
       self.cmdpairs = {
            "!pizza" : self.execute
            }

    def randomTopping(self):
	line = random.choice(open('Resources/toppings.txt').readlines()).rstrip()
        return line

    def execute(self, queue, nick, msg, channel):
        try:
            toppings = int(msg.split()[1])
        except ValueError:
            print "Wrong input for toppings"
            queue.put(("Only number of toppings please", channel))
            return
	except IndexError:
            print "No number of toppings given, randoming amount"
            toppings = random.randint(1,8)

	if toppings < 1 or toppings > 9:
            print "Wrong number of toppings"
	    queue.put(("1-8 toppings please", channel))
            return
       
 	pizzaToppings = []

        while len(pizzaToppings) < toppings:
            topping = self.randomTopping()
            if topping not in pizzaToppings:
                pizzaToppings.append(topping)
	
        
	pizza = ", ".join(pizzaToppings)
        print pizza
	print "executed pizza"
        queue.put((pizza, channel))
