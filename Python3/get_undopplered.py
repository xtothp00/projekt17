import re

def extract_filename(filename):
#                              HDSDR_      20160126 _       205400  Z _             435320 kHz_ RF  .              wav
  pattern_named = re.compile(r'HDSDR_(?P<date>\d{8})_(?P<time>\d{6}).*_(?P<frequency>\d{6})kHz_(RF)\.(?P<extension>\w{3})$')    # REGEX pattern with named subgroups date, time, frequency, extension
  filename_regexed_named = re.search(pattern_named, filename)
  file_parameters = filename_regexed_named.groupdict()

  if file_parameters['extension'] == 'wav':     # filter out non-wav files
    return file_parameters
  else:
    return None
