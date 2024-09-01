from pyannote.audio import Pipeline
from pyannote.audio.pipelines import VoiceActivityDetection
from pyannote.audio import Model
import os

from dotenv import load_dotenv
load_dotenv()

def get_vad_pipeline():
    model = Model.from_pretrained(
            "pyannote/segmentation-3.0", 
    use_auth_token=os.getenv("HUGGINGFACE_TOKEN"))
    vad_pipeline = VoiceActivityDetection(segmentation=model)

    # Set hyperparameters for the pipeline
    HYPER_PARAMETERS = {
    "min_duration_on": 0.0,   # remove speech regions shorter than that many seconds.
    "min_duration_off": 0.0   # fill non-speech regions shorter than that many seconds.
    }
    vad_pipeline.instantiate(HYPER_PARAMETERS)
    return vad_pipeline