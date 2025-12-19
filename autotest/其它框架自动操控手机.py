"""
python uitars_android_u2.py \
    --prompt "打开小红书，搜索人文智能实验室，截图 lab.png" \
    --model humeman/uitars-7b --device cuda:0
"""
import argparse, re, time
from PIL import Image
import uiautomator2 as u2
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

ACTION_RE = re.compile(r'<(\w+)>(.*?)</\1>')

def load_uitars(model_name, device):
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map=device,
        torch_dtype=torch.float16 if "cuda" in device else torch.float32,
        trust_remote_code=True).eval()
    return model, tok

def parse_action(txt):
    return [(a.lower(), p) for a, p in ACTION_RE.findall(txt)]

def execute_u2(actions, d):
    for act, param in actions:
        if act == "tap":
            x, y = map(int, param.split(","))
            d.click(x, y)
        elif act == "type":
            d.send_keys(param)
        elif act == "key":
            code = param.upper()
            if not code.startswith("KEYCODE_"):
                code = "KEYCODE_" + code
            d.press(code)
        elif act == "swipe":
            x1,y1,x2,y2 = map(int, param.split(","))
            d.swipe(x1,y1,x2,y2, 0.2)   # 200ms
        elif act == "wait":
            time.sleep(float(param))
        elif act == "screenshot":
            d.screenshot().save(param)
        else:
            print("[warn] unknown", act)
        time.sleep(0.3)

def main():
    ag = argparse.ArgumentParser()
    ag.add_argument("--prompt", required=True)
    ag.add_argument("--model", default="humeman/uitars-7b")
    ag.add_argument("--device", default="cuda:0")
    args = ag.parse_args()

    print("Loading UI-TARS …")
    model, tok = load_uitars(args.model, args.device)

    d = u2.connect()               # 默认取唯一在线设备；也可指定 serial
    print("Device:", d.info)

    while True:
        img = d.screenshot()       # PIL.Image
        messages = [{"role":"user","content":[
            {"type":"image","image":img},
            {"type":"text","text":args.prompt}
        ]}]
        txt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(txt, return_tensors="pt").to(model.device)

        out = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=False,
            eos_token_id=tok.convert_tokens_to_ids("")
        )
        gen = tok.decode(out[0, inputs.input_ids.shape[1]:], skip_special_tokens=False)
        print(">>", gen.strip())

        acts = parse_action(gen)
        if not acts:
            print("No action parsed, exit.")
            break
        execute_u2(acts, d)
        if any(a[0]=="screenshot" for a in acts):
            break

if __name__ == "__main__":
    main()
