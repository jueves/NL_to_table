from faster_whisper import WhisperModel
import os



DEFAULT_MODEL = os.environ.get("WHISPER_MODEL")
WHISPER_LANG = os.environ.get("WHISPER_LANG")

class Whisper4Bot:
    def __init__(self, bot, default_model=DEFAULT_MODEL):
        self.bot = bot
        self.type = default_model
        self.model = WhisperModel(default_model, device="CPU", compute_type="int8")
        self.available = True
   
    def transcribe(self, message, whisper_prompt):
        '''
        Gets a message with an audio file.
        Returns a duple with model availability (boolean) and audio
        transcription (str) in case the model is available.
        '''
        # Dowload audio file if needed
        file_name = self.get_audio_filename(message)       
        answer = None
        if self.available:
            self.available = False
            self.bot.reply_to(message, "Procesando audio...")
            segments, _ = self.model.transcribe(audio=file_name, language=WHISPER_LANG,
                                                beam_size=5, initial_prompt=whisper_prompt)
            text = ""
            for segment in segments:
                text += segment.text
            print("AUDIO TRANSCRIPTION:\n" + text)
            answer = text
            self.available = True
        return(self.available, answer)
    
    def get_audio_filename(self, message):
        '''
        Gets a message with some type of audio
        Returns file name and language
        '''
        file_info = self.bot.get_file(message.voice.file_id)

        downloaded_file = self.bot.download_file(file_info.file_path)
        file_name = f"user_data/{str(message.from_user.id)}.ogg"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        return(file_name)
    