"""Continuous Android CPU/RAM/storage optimizer for Pocket AI v16.

Normal inference starts at 0.6B and can scale through 0.8B, 1.5B, 1.7B,
2B and 3B before the optional 4B/8B tiers. The 135M models are emergency-only.
"""
from __future__ import annotations
from typing import Dict
MODULE_VERSION=9
MiB=1024**2

COMBINATION_TIERS=[
 {"id":"internal_critical","min_ram":0,"min_free":0,"min_cpu":0,"model":"internal","profile":"ultra_eco"},
 {"id":"emergency_fast_2gb","min_ram":1200*MiB,"min_free":240*MiB,"min_cpu":0,"model":"emergency_fast","profile":"eco"},
 {"id":"emergency_quality_2gb","min_ram":1700*MiB,"min_free":400*MiB,"min_cpu":12,"model":"emergency_quality","profile":"entry"},
 {"id":"fast_0_6b_3gb","min_ram":2800*MiB,"min_free":800*MiB,"min_cpu":24,"model":"fast","profile":"entry"},
 {"id":"fast_0_6b_4gb","min_ram":3500*MiB,"min_free":1050*MiB,"min_cpu":34,"model":"fast","profile":"balanced"},
 {"id":"quality_0_8b_4gb","min_ram":4100*MiB,"min_free":1150*MiB,"min_cpu":38,"model":"quality","profile":"balanced"},
 {"id":"quality_0_8b_6gb","min_ram":5200*MiB,"min_free":1700*MiB,"min_cpu":48,"model":"quality","profile":"performance"},
 {"id":"smart_1_5b_5gb","min_ram":4700*MiB,"min_free":1500*MiB,"min_cpu":42,"model":"smart","profile":"balanced"},
 {"id":"smart_1_5b_6gb","min_ram":5400*MiB,"min_free":1900*MiB,"min_cpu":52,"model":"smart","profile":"performance"},
 {"id":"ultra_1_7b_6gb","min_ram":5300*MiB,"min_free":1700*MiB,"min_cpu":47,"model":"ultra","profile":"balanced"},
 {"id":"ultra_1_7b_8gb","min_ram":7200*MiB,"min_free":2800*MiB,"min_cpu":68,"model":"ultra","profile":"performance"},
 {"id":"advanced_2b_6gb","min_ram":5800*MiB,"min_free":1900*MiB,"min_cpu":50,"model":"advanced","profile":"balanced"},
 {"id":"advanced_2b_8gb","min_ram":7200*MiB,"min_free":2900*MiB,"min_cpu":64,"model":"advanced","profile":"performance"},
 {"id":"prime_3b_8gb","min_ram":6800*MiB,"min_free":2400*MiB,"min_cpu":58,"model":"prime","profile":"balanced"},
 {"id":"prime_3b_8gb_strong","min_ram":7600*MiB,"min_free":3300*MiB,"min_cpu":68,"model":"prime","profile":"performance"},
 {"id":"pro_4b_10gb","min_ram":8600*MiB,"min_free":3800*MiB,"min_cpu":70,"model":"pro","profile":"performance"},
 {"id":"pro_4b_12gb","min_ram":11000*MiB,"min_free":5200*MiB,"min_cpu":80,"model":"pro","profile":"flagship"},
 {"id":"max_8b_12gb","min_ram":12000*MiB,"min_free":6300*MiB,"min_cpu":82,"model":"max","profile":"performance"},
 {"id":"max_8b_16gb","min_ram":15000*MiB,"min_free":8200*MiB,"min_cpu":88,"model":"max","profile":"flagship"},
]
PROFILE_ORDER=["ultra_eco","eco","entry","balanced","performance","flagship"]
BASE_PROFILE={"ultra_eco":(256,8,8,48,1,106),"eco":(384,16,8,80,1,106),"entry":(640,24,16,144,2,104),"balanced":(1280,40,24,256,3,102),"performance":(2048,64,32,416,4,100),"flagship":(3072,80,40,640,6,98)}
MODEL_CAPS={
 "emergency_fast":{"ultra_eco":(384,72,8,8),"eco":(512,96,16,8),"entry":(768,144,24,16),"balanced":(1024,192,32,16),"performance":(1280,224,48,24),"flagship":(1536,240,64,32)},
 "emergency_quality":{"ultra_eco":(384,80,8,8),"eco":(512,112,16,8),"entry":(768,168,24,16),"balanced":(1280,240,40,20),"performance":(1536,280,48,24),"flagship":(1536,280,64,32)},
 "fast":{"ultra_eco":(256,48,8,8),"eco":(384,80,12,8),"entry":(640,144,24,12),"balanced":(1280,256,40,20),"performance":(2048,384,64,32),"flagship":(3072,512,80,40)},
 "quality":{"ultra_eco":(192,40,8,8),"eco":(320,72,12,8),"entry":(512,128,20,12),"balanced":(1024,240,32,16),"performance":(1792,416,48,24),"flagship":(3072,576,64,32)},
 "smart":{"ultra_eco":(128,32,8,8),"eco":(192,48,8,8),"entry":(320,80,16,8),"balanced":(768,176,32,16),"performance":(1536,384,48,24),"flagship":(2560,640,64,32)},
 "ultra":{"ultra_eco":(128,32,8,8),"eco":(160,40,8,8),"entry":(256,64,16,8),"balanced":(640,144,32,16),"performance":(1280,352,48,24),"flagship":(2304,704,64,32)},
 "advanced":{"ultra_eco":(96,24,8,8),"eco":(128,32,8,8),"entry":(192,48,12,8),"balanced":(512,112,24,12),"performance":(1024,288,40,20),"flagship":(2048,640,56,28)},
 "prime":{"ultra_eco":(80,24,8,8),"eco":(112,28,8,8),"entry":(160,40,8,8),"balanced":(384,88,20,10),"performance":(896,224,32,16),"flagship":(1792,512,40,20)},
 "pro":{"ultra_eco":(64,24,8,8),"eco":(96,24,8,8),"entry":(128,32,8,8),"balanced":(320,72,16,8),"performance":(768,192,28,14),"flagship":(1536,448,36,18)},
 "max":{"ultra_eco":(64,24,8,8),"eco":(96,24,8,8),"entry":(128,32,8,8),"balanced":(256,56,12,8),"performance":(640,144,24,12),"flagship":(1280,320,24,12)},
}
def _coarse(total,available,cpu,is64,temp):
 if (not is64) or total<1200*MiB or available<220*MiB:return "ultra_eco"
 if total<2600*MiB or available<500*MiB or cpu<20:return "eco"
 if total<3900*MiB or available<950*MiB or cpu<34:return "entry"
 if total<6500*MiB or available<1900*MiB or cpu<62:return "balanced"
 if total>=9000*MiB and available>=3800*MiB and cpu>=78:return "flagship"
 return "performance"
def _threads_for(cpu,cores,profile):
 spare=max(1,min(6,cores-1 if cores>1 else 1));target=BASE_PROFILE.get(profile,BASE_PROFILE["balanced"])[4]
 if cpu<20:target=1
 elif cpu<40:target=min(target,2)
 elif cpu<60:target=min(target,3)
 elif cpu<78:target=min(target,4)
 if cores<=4:target=min(target,2)
 return max(1,min(target,spare))
def optimize_runtime(*,model,total_ram,available_ram,cpu_score,cores,is_64_bit,temperature=0.0,storage_free=0,battery_percent=100,charging=False,requested="auto")->Dict:
 total=max(0,int(total_ram));free=max(0,int(available_ram));cpu=max(0,min(100,int(cpu_score)));cores=max(1,int(cores));temp=float(temperature or 0.0)
 coarse=_coarse(total,free,cpu,is_64_bit,temp) if requested=="auto" else requested
 if coarse not in BASE_PROFILE:coarse="balanced"
 context,batch,ubatch,out_tokens,_,timeout=BASE_PROFILE[coarse];caps=MODEL_CAPS.get(model,MODEL_CAPS["emergency_fast"])[coarse]
 context=min(context,caps[0]);out_tokens=min(out_tokens,caps[1]);batch=min(batch,caps[2]);ubatch=min(ubatch,caps[3],batch);threads=_threads_for(cpu,cores,coarse);guards=[]
 if free<230*MiB:context,batch,ubatch,out_tokens,threads=128,8,8,32,1;coarse="ultra_eco";guards.append("critical free RAM")
 elif free<360*MiB:context,batch,ubatch,out_tokens,threads=min(context,256),min(batch,12),8,min(out_tokens,56),1;guards.append("low free RAM")
 elif free<520*MiB:context,batch,ubatch,out_tokens=min(context,384),min(batch,16),min(ubatch,8),min(out_tokens,80);guards.append("limited free RAM")
 if temp>=88:threads,context,batch,ubatch,out_tokens=1,128,8,8,24;guards.append("emergency raw thermal sensor")
 elif temp>=78:threads,context,batch,ubatch,out_tokens=1,min(context,256),8,8,min(out_tokens,48);guards.append("critical raw thermal sensor")
 elif temp>=68:threads,batch,out_tokens=min(2,threads),min(batch,20),min(out_tokens,112);guards.append("hot raw thermal sensor")
 if battery_percent and battery_percent<=10 and not charging:threads,out_tokens,context=1,min(out_tokens,72),min(context,384);guards.append("low battery")
 matching=[i for i in COMBINATION_TIERS if i["model"]==model] or [i for i in COMBINATION_TIERS if i["model"]=="internal"];combo=matching[0]
 for item in matching:
  if total>=item["min_ram"] and free>=item["min_free"] and cpu>=item["min_cpu"]:combo=item
 qwen=model in {"fast","quality","smart","ultra","advanced","prime","pro","max"};emergency=model in {"emergency_fast","emergency_quality"}
 return {"requested":requested,"model":model,"resolved":coarse,"combination_id":combo["id"],"threads":max(1,threads),"context":max(64,context),"batch":max(4,batch),"ubatch":max(4,min(batch,ubatch)),"max_tokens":max(24,out_tokens),"timeout":min(106,timeout),"temperature":0.22 if qwen else (0.06 if emergency else 0.12),"top_p":0.88 if qwen else 0.82,"repeat_penalty":1.09 if qwen else 1.14,"memory_budget_bytes":max(80*MiB,int(free*0.68)),"guards":guards,"description":f"{combo['id']} plan: {threads} thread(s), context {context}, batch {batch}, {out_tokens} output tokens."}
def recommend_configuration(scan:dict,compatibility:dict)->Dict:
 total=int(scan.get("ram",{}).get("total",0) or 0);free=int(scan.get("ram",{}).get("available",0) or 0);processor=scan.get("processor",{});cpu=int(processor.get("score",0) or 0);is64=bool(processor.get("is_64_bit"));temp=float(scan.get("thermal",{}).get("maximum_celsius",0) or 0);cores=int(processor.get("logical_cores",1) or 1);battery=scan.get("battery",{});percent=int(battery.get("capacity_percent",100) or 100);charging=str(battery.get("status","")).casefold() in {"charging","full"}
 model="internal";reasons=[]
 if free<180*MiB or not is64:reasons.append("live RAM or architecture requires the internal engine")
 elif compatibility.get("max",{}).get("compatible") and total>=12000*MiB and free>=6300*MiB and cpu>=82:model="max";reasons.append("Qwen3 8B is the strongest sustainable installed match")
 elif compatibility.get("pro",{}).get("compatible") and total>=8600*MiB and free>=3800*MiB and cpu>=70:model="pro";reasons.append("Qwen3 4B fits the live memory and CPU budget")
 elif compatibility.get("prime",{}).get("compatible") and total>=6800*MiB and free>=2400*MiB and cpu>=58:model="prime";reasons.append("Qwen2.5 3.09B is the strongest extended match")
 elif compatibility.get("advanced",{}).get("compatible") and total>=5800*MiB and free>=1900*MiB and cpu>=50:model="advanced";reasons.append("Qwen3.5 2B fits the live budget")
 elif compatibility.get("ultra",{}).get("compatible") and total>=5300*MiB and free>=1700*MiB and cpu>=47:model="ultra";reasons.append("Qwen3 1.7B is the strongest practical compact match")
 elif compatibility.get("smart",{}).get("compatible") and total>=4700*MiB and free>=1500*MiB and cpu>=42:model="smart";reasons.append("Qwen2.5 1.5B fits the live budget")
 elif compatibility.get("quality",{}).get("compatible") and total>=4100*MiB and free>=1150*MiB and cpu>=38:model="quality";reasons.append("Qwen3.5 0.8B is the best bridge for this phone")
 elif compatibility.get("fast",{}).get("compatible") and total>=2800*MiB and free>=800*MiB and cpu>=24:model="fast";reasons.append("Qwen3 0.6B is the regular minimum")
 elif compatibility.get("emergency_quality",{}).get("compatible"):model="emergency_quality";reasons.append("live resources require the 135M quality emergency fallback")
 elif compatibility.get("emergency_fast",{}).get("compatible"):model="emergency_fast";reasons.append("live resources require the minimum 135M emergency fallback")
 else:reasons.append("transformer requirements are not currently satisfied")
 runtime_model=model if model!="internal" else "emergency_fast";plan=optimize_runtime(model=runtime_model,total_ram=total,available_ram=free,cpu_score=cpu,cores=cores,is_64_bit=is64,temperature=temp,battery_percent=percent,charging=charging)
 if total<900*MiB or free<150*MiB or not is64:classifier="micro"
 elif total<1500*MiB or free<280*MiB:classifier="lite"
 elif total<2400*MiB or cpu<22:classifier="balanced"
 elif total<3500*MiB or cpu<42:classifier="standard"
 else:classifier="max"
 if model=="internal":hybrid="off"
 elif model in {"max","pro","prime","advanced","ultra","smart","quality"} and free>=1700*MiB:hybrid="fusion"
 elif model in {"fast","quality","smart","ultra","advanced"}:hybrid="smart"
 else:hybrid="speed"
 return {"gguf_model":model,"classifier_profile":classifier,"runtime_profile":plan["resolved"],"runtime_combination":plan["combination_id"],"runtime_plan":plan,"hybrid_mode":hybrid,"llm_mode":"always" if model!="internal" else "off","selection_reasons":reasons}
