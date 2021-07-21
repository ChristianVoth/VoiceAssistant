import requests
import pyaudio
from deepspeech import Model
import scipy.io.wavfile as wav
import wave
import webrtcvad
import collections
import sys
import signal

from array import array
from struct import pack
import time

WAVE_OUTPUT_FILENAME = "recording.wav"

def handle_int(sig, chunk):
    global leave, got_a_sentence
    leave = True
    got_a_sentence = True

def record_to_file(path, data, sample_width):
    data = pack("<" + ("h" * len(data)), * data)
    wf = wave.open(path, "wb") #If path is a string, open the file by that name, otherwise treat it as a file-like object. Mode can be "wb"=write only mode "rb"= read only mode
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(16000)
    wf.writeframes(data) #Writes audio frames and make sure n frames is correct. It will raise n error if the output stream is not seekable and the total number of frames that have been written after data has been written does not match the previously set value for nframes
    wf.close()
    
def normalize(snd_data):
    #Average the volume out
    MAXIMUM = 32767 #or 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)
    r = array("h")
    for i in snd_data:
        r.append(int(i*times))
    return r

def record_audio():
    #start with pyaudio settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 #Samples per second
    CHUNK_DURATION_MS = 30 #support for 10,20,30ms
    PADDING_DURATION_MS = 1500
    CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000) #chunk to read, how much audio is proccessed at a time
    CHUNK_BYTES = CHUNK_SIZE * 2
    NUM_PADDING_CHUNKS = int(PADDING_DURATION_MS / CHUNK_DURATION_MS)
    NUM_WINDOW_CHUNKS = int(400 / CHUNK_DURATION_MS)
    NUM_WINDOW_CHUNKS_END = NUM_WINDOW_CHUNKS * 2
    
    START_OFFSET = int(NUM_WINDOW_CHUNKS * CHUNK_DURATION_MS * 0.5 * RATE)
    
    vad = webrtcvad.Vad(1) #creating a vad object with the agressiveness mode on 1
    
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels = CHANNELS, rate = RATE, input=True, start = False, frames_per_buffer = CHUNK_SIZE)
    
    got_a_sentence = False
    leave = False
    
    signal.signal(signal.SIGINT, handle_int) #the signal.signal() function allows defining custom handlers to be executed when a signal is received. A small number of default handlers are installed: sigint is translated into a keyboardInterrupt exception if the parent process has not changed it
    
    while not leave:
        ring_buffer = collections.deque(maxlen=NUM_PADDING_CHUNKS)
        triggered = False
        voiced_frames = []
        ring_buffer_flags = [0] * NUM_WINDOW_CHUNKS
        ring_buffer_index = 0
        
        ring_buffer_flags_end = [0] * NUM_WINDOW_CHUNKS_END
        ring_buffer_index_end = 0
        buffer_in = ""
        raw_data = array("h")
        index = 0
        StartTime = time.time()
        print("recording:")
        stream.start_stream()
        
        while not got_a_sentence and not leave:
            chunk = stream.read(CHUNK_SIZE)
            raw_data.extend(array("h",chunk)) #die gelesenen samples werden im array gespeichert
            index += CHUNK_SIZE
            TimeUse = time.time() - StartTime
            
            active = vad.is_speech(chunk, RATE) #is_speech is looking if the chunk is speech or not
            
            sys.stdout.write("1" if active else "_")
            ring_buffer_flags[ring_buffer_index] = 1 if active else 0
            ring_buffer_index += 1
            ring_buffer_index %= NUM_WINDOW_CHUNKS
            
            ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
            ring_buffer_index_end += 1
            ring_buffer_index_end %= NUM_WINDOW_CHUNKS_END
            
            if not triggered:
                ring_buffer.append(chunk)
                num_voiced = sum(ring_buffer_flags)
                if num_voiced > 0.8 * NUM_WINDOW_CHUNKS:
                    sys.stdout.write("Open")
                    triggered = True
                    start_point = index - CHUNK_SIZE * 20
                    ring_buffer.clear()
            else:
                ring_buffer.append(chunk)
                num_unvoiced = NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
                if num_unvoiced > 0.90 * NUM_WINDOW_CHUNKS_END or TimeUse > 6:
                    sys.stdout.write("Close")
                    triggered = False
                    got_a_sentence = True
            sys.stdout.flush()
            
        sys.stdout.write("\n")
            
        stream.stop_stream()
        print("done recording")
        got_a_sentence = False
            
        raw_data.reverse()
        for index in range(start_point):
            raw_data.pop()
        raw_data.reverse()
        raw_data = normalize(raw_data)
        record_to_file("recording.wav", raw_data, 2)
        leave = True
    stream.close()
        
def deepspeech_predict(WAVE_OUTPUT_FILENAME):
    ds = Model("output_graph.tflite")
    ds.enableExternalScorer("kenlm.scorer")
    fs, audio = wav.read("recording.wav")
    
    return ds.stt(audio)

bot_message = ""
message = ""
while bot_message != "Einen schönen Tag":

    record_audio()
    message = deepspeech_predict(WAVE_OUTPUT_FILENAME)

    print("Sending: " + message)

    if message != "":

            r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})

            print("Bot says, ", end = ' ')
            for i in r.json():
                bot_message = i['text']
                print(f"{i['text']}")

            