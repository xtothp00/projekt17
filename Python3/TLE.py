#!/bin/python3

import re
import datetime
import os

#SB KEPS @ AMSAT  $ORB06243.N
#2Line Orbital Elements 06243.AMSAT
PATTERN_START_1  = re.compile(r'SB\s+KEPS\s+@\s+AMSAT\s+\$ORB\d{5}\.[A-Z]')
PATTERN_START_2  = re.compile(r'^2Line')
#1 28897U 05043H   06249.26374724  .00000138  00000-0  38823-4 0  1152
#2 28897 098.1525 146.2174 0016539 282.7486 077.1854 14.59597696 37959
#/EX
PATTERN_END      = re.compile(r'^\/EX')
#FROM WA5QGD FORT WORTH,TX August 31, 2006
PATTERN_DATE     = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1}|\d{2})\,\s+(\d{4})') # Patter to search the date inside the extracted TLE chunk. The regular expresion is split to three groups as the date is writen in the US format: group 1: Month; group 2: day (one or two digits); group 3: year (four digits)
FLAG_BEGINNING_1 = 1 << 0
FLAG_BEGINNING_2 = 1 << 1
FLAG_ENDING      = 1 << 2


# Setting flags on a register passed
# register is the register to modify
# multiple flags can be passed
def set_flag(register, *flag):
  """set_flag(register, flag_1, flag_2, ...)

  Setting one or more flags in a register passed as an argument.
  If no flag is passed the register is not going to be modified.
  """
  if flag:
    for f in flag:
      register |= f
    return register
  else:
# An empty list has been passed
    return register

# Unsetting flags on a register passed
# register is the register to modify
# multiple flags can be passed
def unset_flag(register, *flag):
  """unset_flag(register, flag_1, flag_2, ...)

  Unsetting one or more flags in a register passed as an argument.
  For multiple flags passed they all need to be set in the rigistry
  in order to achive True to be returned.
  If no flag is passed the register is not going to be modified and
  it is being returned as it was passed.
  """
  if flag:
    for f in flag:
      register &= ~f
    return register
  else:
# An empty list has been passed.
    return register

# Checking flags on a register passed
# register is the register to be checked.
# Multiple flags can be passed
def check_flag(register, *flag):
  """check_flag(register, flag_1, flag_2, ...)

    Checking one or more flags in a register passed as an argument.
    If no flag is passed the register 0 is being returned.
  """
  flags = 0

  if flag:
    for f in flag:
     flags |= f
    return bool((register & flags) == (register))
  else:
    return 0

# Checking if the passed line matches the passed pattern.
def check_line(pattern, line_to_check):
  """check_line(pattern, line_to_check)

  Checking of the passed line matched the REGEX pattern.
  """
  return bool(re.search(pattern, line_to_check))

# Appending the line to a string.
def append_line(string, *lines_to_append):
  """append_line(string, *lines_to_append)

  Appending lines passed to the function to the string
  """
  for line in lines_to_append:
    string += line

  return string

# Dumping a set of TLEs files
def dump_to_file(set_of_TLEs, directory='../keps/'):
  '''dump_to_file(set_of_TLEs, [directory='../keps/'])

  The function takes a set of TLEs extracted from the AMSAT e-mail list.
  Each member of the set is written to a file, which name containes the
  date of the TLE file. In case of multiple files per day, the last one
  will be written out overwriting the files written before.
  The function checks the directory if it is available at the CWD. If it
  exists, than the file is witten there. If a file named that exists,
  a new folder is being created.
  Probably the function will be able to handle not just set as parameter,
  but another iterable types. It was not tested due to shortage of available
  time.
  Optional directory parametere can be passed, which can be either
  realtive or absolute.

  '''
  for element in set_of_TLEs:
    date_string = re.search(PATTERN_DATE, element)
    if date_string == None:
      return None
    else:
      date = datetime.datetime.strptime(date_string.group(0), '%B %d, %Y')
      filename = date.strftime('%Y-%m-%d')  + '.amsat.tle'
      directoryname = date.strftime('%Y')

    i = 0      # iteration for the directory name

    while True:
      if os.path.isdir(directoryname):
        full_path = os.path.join(directory, directoryname, filename)
        break
      else:
        if os.path.exists(directoryname):
          if directoryname.find('_') == -1:
            directoryname += '_' + '%02d' %(i)
          else:
            directoryname[:directoryname.rfind('_')] += '_' + '%02d' %(i)
            i += 1
        else:
          full_path = os.path.join(directory, directoryname, filename)

    os.makedirs(os.path.join(directory, directoryname), exist_ok=True)
    tle_file = open(full_path, 'w')
    tle_file.writelines(element)
    tle_file.close()

# Function to look up TLE in the AMSAT mailing list archive.
#
#
def extract_amsat_TLE(AMSAT_maillist_filename, directory='../keps/'):
  '''extract_amsat_TLE(AMSAT_maillist_filename, [directory='../keps/'])
  The mail list file is from http://amsat.org/pipermail/keps/.
  The filename is just the year represented by four digits,
  a period and string "txt" (i.e. 2006.txt).
  Optional directory parametere can be passed, which can be either
  realtive or absolute.
  '''
  f = open(os.path.join(directory, AMSAT_maillist_filename), 'r')
  f_register = 0
  string_TLE = ''
  set_of_string_TLE = set()
  line = f.readline()


  while line:
    if check_line(PATTERN_START_1, line):
      f_register = set_flag(f_register, FLAG_BEGINNING_1)
      line_start_1 = line
      line = f.readline()
      continue
    elif check_flag(f_register, FLAG_BEGINNING_1):
      if check_line(PATTERN_START_2, line):
        f_register = set_flag(f_register, FLAG_BEGINNING_2)
        line_start_2 = line
        line = f.readline()
        string_TLE = append_line(string_TLE, line_start_1, line_start_2)
        continue
      else:
        f_register = unset_flag(f_register, FLAG_BEGINNING_1)
        line = f.readline()
        continue
    else:
      if check_flag(f_register, FLAG_BEGINNING_1, FLAG_BEGINNING_2):
        if check_line(PATTERN_END, line):
          string_TLE = append_line(string_TLE, line)

          set_of_string_TLE.add(string_TLE)

          string_TLE = ''
          f_register = unset_flag(f_register, FLAG_BEGINNING_1, FLAG_BEGINNING_2, FLAG_ENDING)
          line = f.readline()
        else:
          string_TLE = append_line(string_TLE, line)
          line = f.readline()

  return set_of_string_TLE
