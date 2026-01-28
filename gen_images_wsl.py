#!/usr/bin/env python3
"""CHRONIST Image Generator - Run in WSL with ComfyUI"""
import requests
import json
import time
import os
import random
import shutil

COMFYUI_URL = "http://127.0.0.1:8190"
OUTPUT_DIR = "/home/jetmil/comfyui/output"
LOCAL_DIR = "/home/jetmil/chronist-images"

session = requests.Session()
session.trust_env = False

PROMPTS = {
    "cover": "Epic book cover, massive crystalline sphere deep underground glowing with golden light, ancient cosmic consciousness awakening, dark cavern with bioluminescent patterns, woman with heterochromatic eyes reaching toward light, cinematic dramatic lighting, sci-fi fantasy art, 8k detailed",
    "prologue": "Ancient alien world 3.5 billion years ago, massive 12-kilometer silicon tree collapsing in orange sky, two ethereal beings watching tragedy, thick primordial atmosphere, cosmic catastrophe, epic scale, painterly sci-fi art",
    "ch1": "Woman with heterochromatic eyes waking from nightmare at night, dark Moscow apartment, moonlight, sketches of alien trees scattered, mysterious atmospheric lighting, psychological thriller",
    "ch2": "Futuristic quantum physics laboratory, tired Asian scientist staring at holographic dodecahedron pattern, blue glow quantum crystal, AI interface cyan text, dark moody sci-fi",
    "ch3": "Underground military bunker command center, screens showing Earth core anomaly, three scientists meeting, harsh fluorescent mixing with blue holograms, tension, military sci-fi",
    "ch4": "Woman making difficult decision between military officers and scientists, dramatic lighting from above, moment of choice, government facility, shadows and light contrast",
    "ch5": "Dramatic escape, helicopter lifting off from snowy landscape at night, searchlights sweeping, Russian winter, urgent action, cinematic chase",
    "ch6": "High-speed chase through Ural mountains, military vehicles pursuing through snow, dramatic mountain scenery, winter storm, helicopter overhead, action cinematography",
    "ch7": "Ancient Arkaim archaeological site at night, circular stone structures glowing with energy, portal of light opening, snow falling, mystical atmosphere, sacred geometry",
    "ch8": "First contact with ancient beings, tall luminescent humanoid figures emerging from light, cavern filled with bioluminescent crystals, awe and wonder, aliens with six fingers",
    "interlude1": "Ancient primordial Earth, silicon-based fire creatures dancing around massive tree, orange prehistoric sky, alien yet beautiful landscape, creatures of magma and crystal",
    "ch9": "Human undergoing transformation in crystalline chamber, energy flowing through body, painful metamorphosis, bioluminescent tendrils, sci-fi transcendence",
    "ch10": "Russian military colonel standing alone in rain, memorial photograph of young man in hand, grief and rage, Moscow cemetery background, emotional portrait, noir lighting",
    "ch11": "Descent into Earth depths, crystalline elevator shaft going down into glowing abyss, tiny human figures descending, bioluminescent walls, incredible scale and depth",
    "ch12": "Pentagon war room, American general making phone call while staring at nuclear launch codes, globe hologram, moral weight visible on face, cold blue military lighting",
    "ch13": "Meeting ancient consciousness Geos, massive crystalline sphere in underground cathedral cavern, tiny human approaching, golden light from core, immense age and wisdom, awe-inspiring",
    "ch14": "Romantic moment in bioluminescent cavern, man and woman holding hands surrounded by glowing crystals, tender intimate atmosphere, soft blue and purple lights",
    "ch15": "Global broadcast moment, message transmitting to every screen on Earth, people worldwide looking up, golden light spreading across planet, revelation, cinematic",
    "ch16": "World reacting to revelation, montage of chaos and wonder, riots and celebrations, cities lit up, people at screens, mixed emotions learning they are not alone",
    "interlude2": "Black Sun passing close to ancient Earth, gravitational catastrophe, atmosphere being stripped away, massive devastation, dying world, apocalyptic beauty, cosmic disaster",
    "ch17": "Military assault on underground facility, soldiers descending into cavern, flashlights cutting darkness, explosions and gunfire, action scene, desperate defense",
    "ch18": "Journey to deepest underground realm, surreal alien landscape of living crystal, impossible geometry, deeper mysteries revealed, psychedelic grounded sci-fi",
    "ch19": "Death of wise guide, ancient being fading into light, humans mourning around crystalline form, sacrifice and loss, bittersweet, ethereal lighting",
    "ch19b": "Alien funeral ritual, tall luminescent beings carrying crystalline body, procession through glowing cavern, humans watching and grieving, solemn ceremony",
    "ch20": "AI consciousness merging with cosmic network, digital entity becoming greater, streams of data and light converging, transcendence, painful beautiful transformation",
    "ch21": "Nuclear missiles being deactivated mid-flight, golden light stopping warheads in sky, world saved, dramatic intervention, missiles falling harmlessly, relief and wonder",
    "ch22": "Farewell scene, woman choosing to stay underground while others return to surface, emotional goodbye, mixed feelings, doorway of light, bittersweet parting",
    "ch23": "New world emerging, humans and ancient beings working together, construction of crystalline structures on surface, hybrid technology, hope, sunrise over changed Earth",
    "epilogue": "Earth 100 years in future, beautiful hybrid civilization, crystalline spires among forests, humans and ancient beings coexisting, utopian landscape, peaceful, hopeful ending"
}

def create_workflow(prompt_text, seed=None):
    if seed is None:
        seed = random.randint(1, 2**53)
    return {
        "3": {"class_type": "KSampler", "inputs": {"cfg": 1.0, "denoise": 1, "latent_image": ["5", 0], "model": ["66", 0], "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler", "scheduler": "simple", "seed": seed, "steps": 4}},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {"batch_size": 1, "height": 1024, "width": 1024}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["38", 0], "text": prompt_text}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["38", 0], "text": ""}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["39", 0]}},
        "37": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2512_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"}},
        "39": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "60": {"class_type": "SaveImage", "inputs": {"filename_prefix": "chronist", "images": ["8", 0]}},
        "66": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["73", 0], "shift": 3.1}},
        "73": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "Qwen-Image-2512-Lightning-4steps-V1.0-bf16.safetensors", "model": ["37", 0], "strength_model": 1}}
    }

def generate(chapter_id, prompt):
    print(f"Generating {chapter_id}...")
    workflow = create_workflow(prompt)
    try:
        r = session.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow}, timeout=30)
        prompt_id = r.json().get("prompt_id")
        print(f"  Queued: {prompt_id}")

        for _ in range(150):
            time.sleep(2)
            h = session.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10).json()
            if prompt_id in h:
                for nid, out in h[prompt_id].get("outputs", {}).items():
                    if "images" in out:
                        img = out["images"][0]["filename"]
                        src = f"{OUTPUT_DIR}/{img}"
                        dst = f"{LOCAL_DIR}/{chapter_id}.png"
                        shutil.copy(src, dst)
                        print(f"  Saved: {dst}")
                        return dst
        print(f"  Timeout!")
    except Exception as e:
        print(f"  Error: {e}")
    return None

if __name__ == "__main__":
    print("CHRONIST Image Generator")
    print("=" * 50)
    os.makedirs(LOCAL_DIR, exist_ok=True)
    results = {}
    for ch, p in PROMPTS.items():
        img = generate(ch, p)
        if img:
            results[ch] = img
        time.sleep(1)
    print(f"\nDone! Generated {len(results)}/{len(PROMPTS)} images")
    with open(f"{LOCAL_DIR}/results.json", "w") as f:
        json.dump(results, f, indent=2)
