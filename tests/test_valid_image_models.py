"""Cover success paths of explicit model and aspect validators."""
import pytest
from studio.glabs import ImageRequest

@pytest.mark.parametrize('model,ratio', [('nano_banana_pro','16:9'),('nano_banana_2','1:1'),('nano_banana_2_lite','3:4')])
def test_explicit_valid_image_model_and_aspect(model,ratio):
    request=ImageRequest(prompt='image',model=model,aspect_ratio=ratio)
    assert request.model==model and request.aspect_ratio==ratio
