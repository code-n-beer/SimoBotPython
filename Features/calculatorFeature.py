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

    result = self.calculate(msg[1].replace(" ", ""))

    if (not self.isNumber(result)):
      result = "invalid syntax or value too big"

    if result.endswith(".0"):
      result = result[:-2]

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
      formula = (formula[:parenthStart] 
          + str(self.calculate(formula[parenthStart+1:parenthEnd])) 
          + formula[parenthEnd+1:])
      if formula.find("(") != -1: # we're not at the bottom of recursion
        return self.calculate(formula)

    # deal with everything else
    formula = self.handleOperations(formula,
        { "^" : pow })
    formula = self.handleOperations(formula,
        { "*" : self.multiply,
          "/" : self.divide,
          "%" : self.modulo })
    formula = self.handleOperations(formula, 
        { "+" : self.add, 
          "-" : self.subtract })

      
    print formula

    return formula

  def handleOperations(self, formula, operationDict):
    lastOperator = -1
    i = 1
    while i < len(formula):
      if not self.isPartOfFloat(formula[i], formula[i-1]):
        if formula[i] in operationDict.keys():
          curPos = i
          i = i + 1
          while i < len(formula) and self.isPartOfFloat(formula[i], formula[i-1]):
            i = i + 1
          nextOperator = i
          res = ""
          try:
            res = operationDict[formula[curPos]](float(formula[lastOperator+1:curPos]), 
              float(formula[curPos+1:nextOperator]))
          except (ValueError, OverflowError):
            return "fail"
          formula = formula[:lastOperator+1] + str(res) + formula[nextOperator:]
          i = lastOperator + 1
        else:
          lastOperator = i
      i = i + 1

    return formula

  def modulo(self, x, y):
    return x % y

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
