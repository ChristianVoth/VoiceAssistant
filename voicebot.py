import requests
import pyaudio
from deepspeech import Model
import scipy.io.wavfile as wav
import wave



WAVE_OUTPUT_FILENAME = 'testaudio.wav'

def record_audio(WAVE_OUTPUT_FILENAME):
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	RECORD_SECONDS = 3

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

	print("* recording")

	frames = [stream.read(CHUNK) for i in range(0, int(RATE / CHUNK * RECORD_SECONDS))]

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	
def deepspeech_predict(WAVE_OUTPUT_FILENAME):

        
        ds = Model('output_graph.pbmm')
        ds.enableExternalScorer('kenlm.scorer')

        fs, audio = wav.read('testaudio.wav')

        return ds.stt(audio)

bot_message = ""
message = ""
while bot_message != "Einen schönen Tag":

    record_audio(WAVE_OUTPUT_FILENAME)
    message = deepspeech_predict(WAVE_OUTPUT_FILENAME)

    print("Sending: " + message)

    if message != "":

            r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})

            print("Bot says, ", end = ' ')
            for i in r.json():
                bot_message = i['text']
                print(f"{i['text']}")

    else:
        print("Ich konnte Sie nicht verstehen, sprechen Sie erneut")
