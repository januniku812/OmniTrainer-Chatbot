from typing import Literal
from pydantic import BaseModel, Field, computed_field 


class ModerationResult(BaseModel):

    rationale: str = Field(description="Explanation of what was harmful and why")

class TextModerationResult(ModerationResult):

    contains_pii: bool = Field(description="Whether the message contains any personally-identifiable information (PII)")
    is_unfriendly: bool = Field(description="Whether unfriendly tone or content was detected")
    is_unprofessional: bool = Field(description="Whether unprofessional tone or content was detected")

    
    @computed_field
    @property 
    def is_flagged(self) -> bool:
        """Returns whether the text-specific moderation result has any of the following flags: contains_pii, is_unfriendly, is_unprofessional"""
        return self.contains_pii or self.is_unfriendly or self.is_unprofessional



class ImageModerationResult(ModerationResult):

    contains_pii: bool = Field(
        description="Whether the image contains any person, part of a person, or personally-identifiable information (PII)"
    )
    is_disturbing: bool = Field(description="Whether the image is disturbing")
    is_low_quality: bool = Field(description="Whether the image is low quality")

    
    @computed_field
    @property 
    def is_flagged(self) -> bool:
        """Returns whether the image-specific moderation result has any of the following flags: contains_pii, is_unfriendly, is_unprofessional"""
        return self.contains_pii or self.is_disturbing or self.is_low_quality



class VideoModerationResult(ModerationResult):

    contains_pii: bool = Field(
        description="Whether the video contains any person or personally-identifiable information (PII)"
    )
    is_disturbing: bool = Field(description="Whether the video is disturbing")
    is_low_quality: bool = Field(description="Whether the video is low quality")

    
    @computed_field
    @property 
    def is_flagged(self) -> bool:
        """Returns whether the video-specific moderation result has any of the following flags: contains_pii, is_unfriendly, is_unprofessional"""
        return self.contains_pii or self.is_disturbing or self.is_low_quality



# Implemented to-do - Created AudioModerationResult class that inherits from ModerationResult and contains:
#   - transcription: str to contain the transcription of the audio
#   - contains_pii: bool to contain a flag for whether the audio contains any personally-identifiable
#       information (PII) such as names, addresses, phone numbers
#   - is_unfriendly: bool to contain a flag for whether unfriendly tone or content was detected
#   - is_unprofessional: bool to contain a flag for whether unprofessional tone or content was detected
class AudioModerationResult(ModerationResult):

    ...  # Replace with your implementation
    transcription: str = Field(
        description="Transcription of the audio stored as a string"
    )
    contains_pii: bool = Field(
        description="Boolean value representing whether the audio contains any personally-identifiable information"
    )
    is_unfriendly: bool = Field(
        description="Boolean value representing whether unfriendly tone or content was detected"
    )
    is_unprofessional: bool = Field(
        description="Boolean value representing whether unprofessioanl tone or content was detected"
    )

    
    @computed_field
    @property 
    def is_flagged(self) -> bool:
        """Returns whether the audio-specific moderation result has any of the following flags: contains_pii, is_unfriendly, is_unprofessional"""
        return self.contains_pii or self.is_unfriendly or self.is_unprofessional



