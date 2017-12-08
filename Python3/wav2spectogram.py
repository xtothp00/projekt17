import matplotlib
matplotlib.use('Agg')
import numpy as np
import scipy.signal as signal
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import matplotlib.pyplot as plt

def IQ_to_spectogram(filename_IQ='semmi'):
  rate, data = wavfile.read('HDSDR_20160121_003353Z_435320kHz_RF.UD.local.wav', mmap=False)
  data_cmpl = data.view(np.int16).astype(np.float32).view(np.complex64)   # Changing the data type to complex and
  data_cmpl = data_cmpl.reshape(data_cmpl.shape[0] * data_cmpl.shape[1])  # Reshaping to fit the specgram

  plt.specgram(data_cmpl, NFFT=2048, Fs=rate, Fc=435320000)
  plt.title("NO-84")
  plt.ylim(-rate/2, rate/2)
  plt.savefig("NO-84.pdf", bbox_inches='tight', pad_inches=0.5)
  plt.close()
