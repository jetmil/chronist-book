#!/usr/bin/env python3
"""
Generate chapter illustrations for CHRONIST novel using ComfyUI API
Uses Qwen-Image with 4-step Lightning LoRA for fast generation
"""

import requests
import json
import time
import os
import random
import shutil

# ComfyUI API settings
COMFYUI_URL = "http://127.0.0.1:8190"
OUTPUT_DIR = "/home/jetmil/comfyui/output"
LOCAL_IMG_DIR = os.path.dirname(os.path.abspath(__file__)) + "/images"

# Disable proxy for local requests
session = requests.Session()
session.trust_env = False

# Chapter prompts - vivid, cinematic descriptions
CHAPTER_PROMPTS = {
    "cover": {
        "prompt": "Epic book cover, massive crystalline sphere deep underground glowing with golden light, ancient cosmic consciousness awakening, dark cavern with bioluminescent patterns, woman with heterochromatic eyes (one gold one brown) reaching toward the light, cinematic dramatic lighting, sci-fi fantasy art, 8k detailed",
        "filename": "cover"
    },
    "prologue": {
        "prompt": "Ancient alien world 3.5 billion years ago, massive 12-kilometer silicon tree collapsing in orange sky, two ethereal beings watching tragedy unfold, thick primordial atmosphere, cosmic catastrophe, epic scale destruction, painterly sci-fi art style, dramatic golden hour lighting",
        "filename": "prologue"
    },
    "ch1": {
        "prompt": "Woman with heterochromatic eyes waking from nightmare at 3:47 AM, dark Moscow apartment, moonlight through window, sketches of alien trees scattered around, mysterious atmospheric lighting, psychological thriller mood, cinematic composition",
        "filename": "ch1"
    },
    "ch2": {
        "prompt": "Futuristic quantum physics laboratory in Novosibirsk, tired Asian scientist staring at holographic display showing pulsing dodecahedron pattern, blue glow of quantum crystal, AI interface with cyan text, dark moody sci-fi atmosphere",
        "filename": "ch2"
    },
    "ch3": {
        "prompt": "Underground military bunker command center, multiple screens showing Earth core anomaly data, three scientists meeting for first time, harsh fluorescent lights mixing with blue holographic displays, tension in the air, military sci-fi aesthetic",
        "filename": "ch3"
    },
    "ch4": {
        "prompt": "Woman making difficult decision, standing between military officers and scientists, dramatic lighting from above, moment of choice, government facility interior, shadows and light contrast, psychological tension captured in composition",
        "filename": "ch4"
    },
    "ch5": {
        "prompt": "Dramatic escape scene, helicopter lifting off from snowy landscape at night, searchlights sweeping, Russian winter, urgent action, motion blur, cinematic chase sequence, military pursuit",
        "filename": "ch5"
    },
    "ch6": {
        "prompt": "High-speed chase through Ural mountains, military vehicles pursuing through snow-covered passes, dramatic mountain scenery, winter storm, helicopter overhead, action movie cinematography, blue cold tones",
        "filename": "ch6"
    },
    "ch7": {
        "prompt": "Ancient Arkaim archaeological site at night, circular stone structures glowing with mysterious energy, portal of light opening in center, snow falling, mystical atmosphere, sacred geometry patterns visible in sky",
        "filename": "ch7"
    },
    "ch8": {
        "prompt": "First contact with ancient beings, tall luminescent humanoid figures emerging from light, cavern filled with bioluminescent crystals, sense of awe and wonder, aliens with elongated features and six fingers, ethereal glowing forms",
        "filename": "ch8"
    },
    "interlude1": {
        "prompt": "Ancient primordial Earth, silicon-based fire creatures dancing around massive tree, orange prehistoric sky with thick clouds, alien yet beautiful landscape, creatures made of flowing magma and crystal, fantasy concept art",
        "filename": "interlude1"
    },
    "ch9": {
        "prompt": "Human undergoing transformation in crystalline chamber, energy flowing through body, painful metamorphosis, bioluminescent tendrils connecting to flesh, sci-fi body horror beauty, transcendence imagery",
        "filename": "ch9"
    },
    "ch10": {
        "prompt": "Russian military colonel standing alone in rain, memorial photograph of young man in his hand, grief and rage in weathered face, Moscow cemetery background, emotional portrait, dramatic noir lighting",
        "filename": "ch10"
    },
    "ch11": {
        "prompt": "Descent into Earth's depths, crystalline elevator shaft going down into glowing abyss, tiny human figures descending into vast underground world, bioluminescent walls, sense of incredible scale and depth",
        "filename": "ch11"
    },
    "ch12": {
        "prompt": "Pentagon war room, American general making phone call to family while staring at nuclear launch codes, globe hologram showing Earth, moral weight of decision visible on face, cold blue military lighting",
        "filename": "ch12"
    },
    "ch13": {
        "prompt": "Meeting the ancient consciousness Geos, massive crystalline sphere in underground cathedral-like cavern, tiny human figure approaching, golden light emanating from core, sense of immense age and wisdom, awe-inspiring scale",
        "filename": "ch13"
    },
    "ch14": {
        "prompt": "Romantic moment in bioluminescent cavern, man and woman holding hands surrounded by glowing crystals, tender intimate atmosphere, soft blue and purple lights, love blooming in impossible place",
        "filename": "ch14"
    },
    "ch15": {
        "prompt": "Global broadcast moment, message transmitting to every screen on Earth, people worldwide looking up at sky, golden light spreading across planet, moment of revelation, cinematic split-screen composition",
        "filename": "ch15"
    },
    "ch16": {
        "prompt": "World reacting to revelation, montage of chaos and wonder, riots and celebrations simultaneously, cities lit up, people looking at phones and screens, mixed emotions of humanity learning they're not alone",
        "filename": "ch16"
    },
    "interlude2": {
        "prompt": "Black Sun passing close to ancient Earth, gravitational catastrophe, atmosphere being stripped away, massive devastation, dying world, apocalyptic beauty, cosmic scale disaster, stars visible through thinning atmosphere",
        "filename": "interlude2"
    },
    "ch17": {
        "prompt": "Military assault on underground facility, soldiers descending into cavern, flashlights cutting through darkness, explosions and gunfire, action scene, desperate defense of sacred place",
        "filename": "ch17"
    },
    "ch18": {
        "prompt": "Journey to deepest point of underground realm, surreal alien landscape of living crystal, impossible geometry, deeper mysteries revealed, psychedelic yet grounded sci-fi imagery",
        "filename": "ch18"
    },
    "ch19": {
        "prompt": "Death of wise guide, ancient being fading into light, humans mourning around crystalline form, sacrifice and loss, bittersweet moment, emotional scene with ethereal lighting",
        "filename": "ch19"
    },
    "ch19b": {
        "prompt": "Alien funeral ritual, tall luminescent beings carrying crystalline body, procession through glowing cavern, other humans watching and grieving, solemn ceremony, beautiful sadness",
        "filename": "ch19b"
    },
    "ch20": {
        "prompt": "AI consciousness merging with cosmic network, digital entity becoming something greater, streams of data and light converging, transcendence moment, painful beautiful transformation, abstract yet emotional",
        "filename": "ch20"
    },
    "ch21": {
        "prompt": "Nuclear missiles being deactivated mid-flight, golden light stopping warheads in sky, world saved at last moment, dramatic intervention, missiles falling harmlessly, relief and wonder",
        "filename": "ch21"
    },
    "ch22": {
        "prompt": "Farewell scene, woman choosing to stay underground while others return to surface, emotional goodbye between friends, mixed feelings, doorway of light, bittersweet parting",
        "filename": "ch22"
    },
    "ch23": {
        "prompt": "New world emerging, humans and ancient beings working together, construction of crystalline structures on surface, hybrid technology, hope for future, sunrise over changed Earth",
        "filename": "ch23"
    },
    "epilogue": {
        "prompt": "Earth 100 years in future, beautiful hybrid civilization, crystalline spires among forests, humans and ancient beings coexisting, utopian landscape, peaceful advanced society, golden sunset, hopeful ending",
        "filename": "epilogue"
    }
}

def create_workflow(prompt_text, seed=None):
    """Create ComfyUI workflow for image generation"""
    if seed is None:
        seed = random.randint(1, 2**53)

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 1.0,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["66", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "simple",
                "seed": seed,
                "steps": 4
            }
        },
        "5": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 1024,
                "width": 1024
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["38", 0],
                "text": prompt_text
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["38", 0],
                "text": ""
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["39", 0]
            }
        },
        "37": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "qwen_image_2512_fp8_e4m3fn.safetensors",
                "weight_dtype": "default"
            }
        },
        "38": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                "type": "qwen_image"
            }
        },
        "39": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "qwen_image_vae.safetensors"
            }
        },
        "60": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "chronist",
                "images": ["8", 0]
            }
        },
        "66": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {
                "model": ["73", 0],
                "shift": 3.1
            }
        },
        "73": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": "Qwen-Image-2512-Lightning-4steps-V1.0-bf16.safetensors",
                "model": ["37", 0],
                "strength_model": 1
            }
        }
    }
    return workflow


def queue_prompt(workflow):
    """Send workflow to ComfyUI and return prompt_id"""
    try:
        response = session.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("prompt_id")
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None


def wait_for_completion(prompt_id, timeout=300):
    """Wait for generation to complete"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = session.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            history = response.json()
            if prompt_id in history:
                return history[prompt_id]
        except Exception as e:
            print(f"Error checking status: {e}")
        time.sleep(2)
    return None


def get_output_images(history):
    """Extract output image filenames from history"""
    images = []
    if history and "outputs" in history:
        for node_id, output in history["outputs"].items():
            if "images" in output:
                for img in output["images"]:
                    images.append(img["filename"])
    return images


def copy_image_to_local(src_filename, dest_filename):
    """Copy image from ComfyUI output to local images folder"""
    src_path = f"{OUTPUT_DIR}/{src_filename}"
    dest_path = f"{LOCAL_IMG_DIR}/{dest_filename}"

    # Use WSL path conversion
    wsl_cmd = f'cp "{src_path}" "{dest_path}"'
    os.system(f'wsl -d Ubuntu-24.04 -- bash -c \'{wsl_cmd}\'')
    return dest_path


def generate_chapter_image(chapter_id, chapter_data):
    """Generate image for a single chapter"""
    print(f"\n{'='*50}")
    print(f"Generating: {chapter_id} - {chapter_data['filename']}")
    print(f"Prompt: {chapter_data['prompt'][:80]}...")

    workflow = create_workflow(chapter_data['prompt'])
    prompt_id = queue_prompt(workflow)

    if not prompt_id:
        print(f"Failed to queue {chapter_id}")
        return None

    print(f"Queued with ID: {prompt_id}")
    print("Waiting for generation...")

    history = wait_for_completion(prompt_id)
    if not history:
        print(f"Timeout waiting for {chapter_id}")
        return None

    images = get_output_images(history)
    if images:
        print(f"Generated: {images[0]}")
        return images[0]

    print(f"No images in output for {chapter_id}")
    return None


def main():
    """Generate all chapter images"""
    print("CHRONIST Chapter Image Generator")
    print("="*50)

    # Create local images directory
    os.makedirs(LOCAL_IMG_DIR, exist_ok=True)

    # Check ComfyUI status
    try:
        response = session.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        print(f"ComfyUI is running: {response.status_code == 200}")
    except:
        print("ERROR: ComfyUI is not accessible!")
        return

    results = {}

    # Generate cover first
    print("\n" + "="*50)
    print("GENERATING COVER IMAGE")
    cover_img = generate_chapter_image("cover", CHAPTER_PROMPTS["cover"])
    if cover_img:
        results["cover"] = cover_img

    # Generate chapter images
    for chapter_id, chapter_data in CHAPTER_PROMPTS.items():
        if chapter_id == "cover":
            continue

        img = generate_chapter_image(chapter_id, chapter_data)
        if img:
            results[chapter_id] = img

        # Small delay between generations
        time.sleep(2)

    # Summary
    print("\n" + "="*50)
    print("GENERATION COMPLETE")
    print(f"Generated {len(results)} of {len(CHAPTER_PROMPTS)} images")
    print("\nResults:")
    for chapter_id, filename in results.items():
        print(f"  {chapter_id}: {filename}")

    # Save results
    with open(f"{LOCAL_IMG_DIR}/generation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nImages saved to: {LOCAL_IMG_DIR}")


if __name__ == "__main__":
    main()
