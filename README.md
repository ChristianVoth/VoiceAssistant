
# Voice Assistant

## Komponenten

Speech-to-text (STT) - Eine Sprachverarbeitungskomponente, die Benutzereingaben in einem Audioformat aufnimmt
und eine Textdarstellung davon erzeugt

NLU & Dialogue management - Eine Komponente die Benutzereingaben im Textformat aufnimmt und strukturierte Daten
(Absichten und Enitäten) extrahiert, die dem Assistenten helfen, die Wünsche des Benutzers zu verstehen

Dialogue management - Eine Komponente, die festgelegt, wie ein Assistent in einem bestimmten Status der
Konversation reagieren soll, und diese Antwort in einem Textformat generiert.

Text-to-speech (TTS) - Eine Komponente, die die Antwort des Assistenten in einem Textformat aufnimmt
und eine Sprachdarstellung davon erstellt, die dann an den Benutzer zurückgesendet wird

## Installation der einzelnen Komponenten

### Es wird empfohlen alle Installationen in einem `virtual environment` durchzuführen

### Speech-to-text mittels Mozilla Deepspeech

`pip3 install deepspeech`

Mozilla DeepSpeech ist eine Open-Source Speech-to-Text-Engine, die in Echtzeit auf Geräten ausgeführt werden kann.
Die Spracherkennung findet vollständig offline statt.

Für das benutzen von DeepSpeech werden Sprachmodelle benötigt.
In diesem Projekt werden die von Herrn Agarwal und von Herrn Zesch veröffentlichen deutschen Sprachmodelle verwendet.
Die Auswahl der richtigen Sprachmodelle ist abhängig von der Mozilla Deepspeech Version, sowie der benutzten Plattform.

[Quelle der Sprachmodelle](https://github.com/AASHISHAG/deepspeech-german)

## NLU & Dialogue Management mittels Rasa

#### Installation für Linux and Mac

`pip install rasa`

Rasa ist ein Open-Source-Framework für maschinelles Lernen für automatisierte 
text- und sprachbasierte Konversationen.

#### Rasa für den Raspberry Pi

Rasa besitzt kein offizielles Docker image for ARM, sodass auf Alternativen zurückgegriffen werden musste.

Für die Installation auf einem Raspberry Pi empfehle ich das Projekt von Herrn Koen Vervloesem.

[Projekt Rasa Docker image for ARM von Koen Vervloesem](https://hub.docker.com/r/koenvervloesem/rasa)

Für die Installation einfach dem Github ReadMe folgen.

## Verwendung des Rasa Bots und des vorhandenen Models

`git clone https://github.com/ChristianVoth/Voicebot.git`

`cd Voicebot`

#### Trainiere das NLU und die dialogue models

`rasa train`

#### Teste Rasa ohne Spracherkennung durch:

`rasa shell`

### Wichtig ! Für die Benutzung des Bots ist ein einmaliges Training von nöten

### Für die Benutzung des Bots mit Sprache wichtige Downloads und weitere Installationen

#### Deutsche Sprachmodelle für DeepSpeech

Downloaden Sie die scorer und pbmm Datei für die passende DeepSpeech Version und fügen Sie diese dem Voicebot Ordner hinzu.

[Quelle der language models](https://github.com/AASHISHAG/deepspeech-german)

#### Pyaudio
`pip install Pyaudio`

#### Request
`pip install requests`

#### Wave
`pip install wave`

#### Webrtcvad

Je nachdem ob Sie den Bot mit Voice Activity Detection oder ohne nutzen wollen, wird Webrtcvad benötigt.

`pip install webrtcvad`

## Konsolen Befehle

### Informationen für Raspberry Pi

Auf dem Raspberry Pi sind alle Installationen für die Ausführung im Virtual Environment `voiceassistant` bereits durchgeführt.

Dieses bitte vor den Durchführen der folgenden Befehle aktivieren.

#### Starten Sie rasa

`rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml`

Befehl für Raspberry Pi im Ordner `voicebot`

`docker-compose run rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml`
 
#### Starten sie den Rasa Action Server

`rasa run actions`

Befehl für Raspberry Pi im Ordner `voicebot`

`docker-compose run rasa run actions`

#### Führen Sie die Voicebot.py aus

`python voicebot.py`



