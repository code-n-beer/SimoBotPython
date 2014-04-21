# vim: set fileencoding=UTF-8 :
import re

class calculatorFeature:

  def __init__(self):
    self.cmdpairs = {
        "!c" : self.execute
        }

  def execute(self, queue, nick, msg, channel):
    msg = msg.strip().split(" ", 1)
    if len(msg) < 2:
      queue.put(("nothing to calculate", channel))

    result = self.calculate(msg[1])
    print result
    queue.put((str(result), channel))

  def calculate(self, formula):
    if self.isNumber(formula):
      return formula

    if not formula:
      return ""

    # deal with parenthesis
    parenthStart = formula.find("(")
    if parenthStart > -1:
      stack = [parenthStart]
      i = parenthStart + 1
      while stack:
        if formula[i] == "(":
          stack.append(i)
        elif formula[i] == ")":
          stack.pop()
          parenthEnd = i
        i = i + 1
      formula = formula[:parenthStart] + str(self.calculate(formula[parenthStart+1:parenthEnd])) + formula[parenthEnd+1:]
      if formula.find("(") != -1: # we're not at the bottom of recursion
        return self.calculate(formula)

    # deal with everything else
    formula = self.handleOperation(formula, "*", self.multiply)
    formula = self.handleOperation(formula, "/", self.divide)
    formula = self.handleOperation(formula, "+", self.add)
    formula = self.handleOperation(formula, "-", self.subtract)
      
    print formula

    return formula

  def handleOperation(self, formula, operationString, operationFunc):
    lastOperator = -1
    i = 1
    while i < len(formula):
      if not self.isPartOfFloat(formula[i], formula[i-1]):
        if formula[i] == operationString:
          curPos = i
          i = i + 1
          while i < len(formula) and self.isPartOfFloat(formula[i], formula[i-1]):
            i = i + 1
          nextOperator = i
          print "lastOperator: %s" %lastOperator
          print "curPos: %s" %curPos
          print "nextOperator: %s" %nextOperator
          print "float error with: %s" %formula[lastOperator+1:curPos]
          if lastOperator + 1 == curPos: # fixes a bug with subtraction
            break
          float1 = float(formula[lastOperator+1:curPos])
          float2 = float(formula[curPos+1:nextOperator])
          res = operationFunc(float(formula[lastOperator+1:curPos]), float(formula[curPos+1:nextOperator]))
          formula = formula[:lastOperator+1] + str(res) + formula[nextOperator:]
          i = lastOperator
        else:
          lastOperator = i
      i = i + 1

    return formula

  def multiply(self, x, y):
    return x * y

  def divide(self, x, y):
    if y == 0:
      return 0
    return x / y

  def add(self, x, y):
    return x + y
  
  def subtract(self, x, y):
    return x - y
  
  def isPartOfFloat(self, char, prevChar):
    return char.isdigit() or char == "." or (char == "-" and not prevChar.isdigit())

  def isNumber(self, s):
    try:
      float(s)
      return True
    except ValueError:
      return False
