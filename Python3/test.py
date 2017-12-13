import get_undopplered as gud
import wav2spectrogram as w2s
import os

def process_directory(directory_IQ='../NO-83', offset_corr=False):
  #filename_IQ
  satellite_name      = 'NO-83'
  satellite_frequency = '435350000'
  directory_IQ        = '../NO-83'
  directory_TLE       = '../keps'
  location_SDR        = 'lat=49.173238,lon=16.961292,alt=263.73'

  files_IQ = os.listdir(directory_IQ)

  for file_IQ in files_IQ:
    parameters_file_IQ = gud.extract_IQ_filename(file_IQ)
    print(type(parameters_file_IQ))
    if (type(parameters_file_IQ) == type(dict())):
      if (parameters_file_IQ.get('extension') == 'wav'):
#        print(file_IQ)
        UD_file_IQ = (gud.undoppler_it(file_IQ, satellite_name, satellite_frequency, directory_IQ, directory_TLE, location_SDR, offset_corr))
        if type(UD_file_IQ) == type(str()):
#          print('proces directory: ' + UD_file_IQ + str(type(UD_file_IQ)))
          w2s.IQ_to_spectrogram(gud.undoppler_it(file_IQ, satellite_name, satellite_frequency, directory_IQ, directory_TLE, location_SDR, offset_corr))
          w2s.IQ_to_spectrogram(os.path.join(directory_IQ, file_IQ))



#  for file_IQ in os.listdir(directory_IQ):
#    if ((file_IQ.split('.')[-1] == 'wav') & ~((file_IQ.split('.')[-2] == 'UD') | (file_IQ.split('.')[-2] == 'OC'))):
#      processed_IQ += 1
#      print(file_IQ)
#      file_processed_IQ = gud.undoppler_it(file_IQ, satellite_name, satellite_frequency, directory_IQ, directory_TLE, location_SDR, offset_corr)
#      print((100.0 * processed_IQ) / counted_IQ)
#      if file_processed_IQ != None:
#        w2s.IQ_to_spectogram(file_processed_IQ)
#        w2s.IQ_to_spectogram(os.path.join(directory_IQ, file_IQ))
