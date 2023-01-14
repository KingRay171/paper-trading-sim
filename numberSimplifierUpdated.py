# numberSimplifier method simplifies large numbers, such as 152682054 to 152.682 M
def numberSimplifier(num, should_round):
  # Trillion simplifier
  if (num >= 1000000000000):
    num /= 1000000000000
    if (should_round):
      num = round(num, 2)

    return str(num) + ' T'
    
  # Billion simplifier
  if (num >= 1000000000):
    num /= 1000000000
    if (should_round):
      num = round(num, 2)

    return str(num) + ' B'

  # Million simplifier
  if (num >= 1000000):
    num /= 1000000
    if (should_round):
      num = round(num, 2)

    return str(num) + ' M'


# numberDesimplifier method simplifies large numbers, such as 152.682 M to 152.682 M
def numberDesimplifier(num):
  number = float(num.split()[0])
  number_type = num.split()[1]
  # Trillion Desimplifier
  if (number_type == 'T'):
    number *= 1000000000000
    return number
    
  # Billion Desimplifier
  if (number_type == 'B'):
    number *= 1000000000
    return number

  # Million Desimplifier
  if (number_type == 'M'):
    num *= 1000000
    return number
