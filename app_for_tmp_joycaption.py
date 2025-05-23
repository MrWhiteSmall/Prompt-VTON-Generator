import torch
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration
# torch==2.2.2 可以解决 RuntimeError: "triu_tril_cuda_template" not implemented for 'BFloat16'
# transformers==4.44
# 运行所需  18GB
IMAGE_PATH = "/root/lsj/IMAGDressing-main/assets/images/face/1.jpg"
PROMPT = "Write a long descriptive caption for this image in a formal tone."
MODEL_NAME = "/root/lsj/checkpoints/llama-joycaption-alpha-two-hf-llava"


# Load JoyCaption
# bfloat16 is the native dtype of the LLM used in JoyCaption (Llama 3.1)
# device_map=0 loads the model into the first GPU
processor = AutoProcessor.from_pretrained(MODEL_NAME)
llava_model = LlavaForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype="bfloat16", device_map=0)
llava_model.eval()

def get_prompt_by_img_path(img_path):
    with torch.no_grad():
        # Load image
        image = Image.open(img_path)

        # Build the conversation
        convo = [
            {
                "role": "system",
                "content": "You are a helpful image captioner.",
            },
            {
                "role": "user",
                "content": PROMPT,
            },
        ]

        # Format the conversation
        # WARNING: HF's handling of chat's on Llava models is very fragile.  This specific combination of processor.apply_chat_template(), and processor() works
        # but if using other combinations always inspect the final input_ids to ensure they are correct.  Often times you will end up with multiple <bos> tokens
        # if not careful, which can make the model perform poorly.
        convo_string = processor.apply_chat_template(convo, tokenize = False, add_generation_prompt = True)
        assert isinstance(convo_string, str)

        # Process the inputs
        inputs = processor(text=[convo_string], images=[image], return_tensors="pt").to('cuda')
        inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

        # torch==2.2.2 可以解决 RuntimeError: "triu_tril_cuda_template" not implemented for 'BFloat16'
        # Generate the captions
        generate_ids = llava_model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            suppress_tokens=None,
            use_cache=True,
            temperature=0.6,
            top_k=None,
            top_p=0.9,
        )[0]

        # Trim off the prompt
        generate_ids = generate_ids[inputs['input_ids'].shape[1]:]

        # Decode the caption
        caption = processor.tokenizer.decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        caption = caption.strip()
        # print(caption)
    return caption
    '''
    This is a digital collage featuring 16 individuals, 
    each wearing a different t-shirt with a rainbow-colored design. 
    The individuals, representing various ethnicities and genders, 
    stand against a plain white background. The t-shirts, 
    in colors such as black, red, yellow, and blue, 
    display a rainbow graphic and text. The subjects are arranged in a 4x4 grid, 
    with names in Chinese characters above each row and column.
    '''
    '''
    This photograph features a young, light-skinned woman with long, 
    straight, light brown hair, standing against a plain white background. 
    She wears a cropped, light blue button-up shirt with large front pockets, 
    unbuttoned to reveal a white tank top underneath. Her pants are loose-fitting, 
    light gray sweatpants with an elastic waistband. She has a neutral expression 
    and stands with her hands casually in her pockets. 
    The image is minimalist, focusing on her attire and relaxed posture.
    '''
