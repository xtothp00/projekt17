import re
import datetime, pytz
import os, pty
import subprocess, shlex
import pymediainfo
import wav2spectrogram as w2s

# Function to get some information from the IQ sample filename.
def extract_IQ_filename(filename, directory='../NO-84'):
  '''extract_IQ_filename(filename, [directory='../NO-84'])

  This function is extracting the filename of which pattern
  will be the same in the future, or the REGEX needs to be changed.
  The function will return a dictionary conaning:
  *date       //YYYYMMDD//
  *time       //HHMMSS//
  *frequency  //CCCMMM//[kHz]
  *extension  //re.(\w{3})//e.g. wav
  If the file is not ending with 'wav', then instead of a dictionary
  None is returned.
  '''
# How the regex is built -- hint from a filename.
#                              HDSDR_      20160126 _       205400  Z _             435320 kHz_ RF  .              wav
  pattern_named = re.compile(r'HDSDR_(?P<date>\d{8})_(?P<time>\d{6}).*_(?P<frequency>\d{6})kHz_(RF)\.(?P<extension>\w{3})$')    # REGEX pattern with named subgroups date, time, frequency, extension
  filename_regexed_named = re.search(pattern_named, filename)
  if filename_regexed_named != None:
    file_parameters = filename_regexed_named.groupdict()

    if file_parameters['extension'] == 'wav':     # filter out non-wav files
      return file_parameters
    else:
      return None
  else:
    print(filename_regexed_named)

# A little 'key' function for sorting TLE files with sorted()
def key_function_TLE(date_IQ, date_TLEs):
  return abs(date_IQ - date_TLEs)

def find_TLE_for_IQ_file(filename_IQ, directory_TLE='../keps/'):
  '''find_TLE_for_IQ_file(filename_IQ, [directory_TLE='../keps/'])

  This function is returning the best matching TLEs file
  based on the IQ filename given and the date encoded in it.
  The best match means the least difference between the dates
  indicated by the names of the TLEs and IQ files.
  '''
  parameters_IQ = extract_IQ_filename(filename_IQ)
  if parameters_IQ != None:

    date_IQ = datetime.datetime.strptime(parameters_IQ.get('date'), '%Y%m%d')
    directory_path_TLEs = os.path.join(directory_TLE, str(date_IQ.year))
    pattern_TLE_file = re.compile('%d-%02d-' % (date_IQ.year, date_IQ.month))
    TLEs = list()     # Empty list for TLEs file

    for i in os.listdir(directory_path_TLEs):
      if bool(re.search(pattern_TLE_file, i)):
        TLEs.append(i)
    TLEs = sorted(TLEs, key=lambda TLE: abs(date_IQ - datetime.datetime.strptime(TLE[:10], '%Y-%m-%d')))

    return TLEs[0]
  else:
    return None

# Function used for undoing the doppler frequency shift using the doppler application called by os.system
def undoppler_it(filename_IQ, satellite_name='NO-84', satellite_frequency='435350000', directory_IQ='../NO-84', directory_TLE='../keps', location_SDR='lat=49.173238,lon=16.961292,alt=263.73', offset_corr=False):
  '''undoppler_it(filename_IQ, [satellite_name='NO-84', satellite_frequency='435350000', directory_IQ='../NO-84', directory_TLE='../keps', location_SDR='lat=49.173238,lon=16.961292,alt=263.73']):

  Only one paremeter is requered not to get an error, but not all time
  will it make sense. It is due to the fact that the optional parameters
  are used only for the purpose of the testing.
  '''
  filename_TLE = find_TLE_for_IQ_file(filename_IQ, directory_TLE)

  if filename_TLE != None:
    parameters_IQ = extract_IQ_filename(filename_IQ)
    mediainfo_IQ  = pymediainfo.MediaInfo.parse(os.path.join(directory_IQ, filename_IQ))
    mediainfo_IQ_tracks = mediainfo_IQ.tracks
    audio = mediainfo_IQ_tracks[1]
    audio_dict = audio.to_data()

    local_TZ = pytz.timezone('Europe/Prague')
    naive_datetime_IQ = datetime.datetime.strptime(parameters_IQ.get('date') + parameters_IQ.get('time'), '%Y%m%d%H%M%S')
    local_datetime_IQ = local_TZ.localize(naive_datetime_IQ, is_dst=None)
    utc_datetime_IQ = local_datetime_IQ.astimezone(pytz.utc)

    samplerate = '--samplerate ' + str(audio_dict.get('sampling_rate')) + ' '
    if (int(audio_dict.get('resolution')) == 16) & (audio_dict.get('format_settings') == 'Little / Signed'):
      intype   = '--intype i16 '
      outtype  = '--outtype i16 '
    else:           #in case of strange Wave format, e.g. float samples
      print('Format yet not tested: ')
      print(' * reslution:      ', audio_dict.get('resolution'))
      print(' * format_settings:', audio_dict.get('format_settings'))
      return 1
    tlefile    = '--tlefile '   + os.path.join(directory_TLE, filename_TLE[:4], filename_TLE) + ' '
    tlename    = '--tlename '   + satellite_name                     + ' '
    location   = '--location '  + location_SDR                       + ' '
    frequency  = '--frequency ' + satellite_frequency                + ' '
    time       = '--time '      + local_datetime_IQ.isoformat()[:-6] + ' '
    infile     = os.path.join(directory_IQ, filename_IQ)             + ' '
#   for i in filename_IQ.split('.')[:-1]:
#     filename+= i
    if offset_corr:
      outfile    = os.path.join(directory_IQ, w2s.join(filename_IQ.split('.')[0:-1]) + '.UD.OC.' + filename_IQ.split('.')[-1])
    else:
      outfile    = os.path.join(directory_IQ, w2s.join(filename_IQ.split('.')[0:-1]) + '.UD.' + filename_IQ.split('.')[-1])

    sox_cmd_rbche = '--rate ' + str(audio_dict.get('sampling_rate')) + ' --bits 16 --channels 2 --encoding signed-integer '
    sox_cmd_out = 'sox ' + sox_cmd_rbche + ' --type raw - '        + sox_cmd_rbche + ' --type wav '  + outfile
    sox_cmd_inp = 'sox ' + sox_cmd_rbche + ' --type wav ' + infile + sox_cmd_rbche + ' --type raw -'

    if offset_corr:
      offset = int(satellite_frequency) - (1000 * int(parameters_IQ.get('frequency')))
      offset = '--offset %d ' %(offset)
      doppler_cmd = 'doppler track '+ samplerate + intype + outtype + tlefile + tlename + location + frequency + time + offset
    else:
      doppler_cmd = 'doppler track '+ samplerate + intype + outtype + tlefile + tlename + location + frequency + time

    full_command_doppler = sox_cmd_inp + ' | ' + doppler_cmd + ' | ' + sox_cmd_out

    os.system (full_command_doppler)
    print(full_command_doppler)
    print('undoppler: ' + outfile + str(type(outfile)))
    return outfile

  else:
    return None
