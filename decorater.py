# WHY = make it easy to pass the results of a function to another function

class Car:
  wheels = 4

  def __init__(self, arg1):
    self.color = arg1
  
  def __call__(self, func):
    self.color = func()

  def paintCar(self, arg1):
    self.color = arg1

  def details(self):
    print('color =', self.color)

car1 = Car('red')
car1.paintCar('blue')

@car1
def changeColorWithSemantic():
  return 'yellow'

car1.details()


