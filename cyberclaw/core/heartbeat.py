import os
import json
import asyncio
from datetime import datetime, timedelta
from .config import TASKS_FILE
from .bus import task_queue
from .tools.builtins import tasks_lock 

async def pacemaker_loop(check_interval: int = 10):
    """
    后台心脏起搏器协程（带并发锁和循环任务续期功能）
    """
    while True:
        await asyncio.sleep(check_interval)
        
        if not os.path.exists(TASKS_FILE):
            continue
            
        now = datetime.now()
        pending_tasks = []
        triggered_tasks = []

        with tasks_lock:
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        continue
                    tasks = json.loads(content)
            except Exception:
                continue
                
            if not tasks:
                continue

            for t in tasks:
                try:
                    target_dt = datetime.strptime(t["target_time"], "%Y-%m-%d %H:%M:%S")
                    if now >= target_dt:

                        triggered_tasks.append(t)

                        repeat_freq = t.get("repeat")
                        if repeat_freq:
                            repeat_count = t.get("repeat_count")
                            

                            if repeat_count is not None:
                                if repeat_count <= 1:
                                    continue
                                else:
                                    t["repeat_count"] = repeat_count - 1


                            if repeat_freq == "hourly":
                                next_dt = target_dt + timedelta(hours=1)
                            elif repeat_freq == "daily":
                                next_dt = target_dt + timedelta(days=1)
                            elif repeat_freq == "weekly":
                                next_dt = target_dt + timedelta(days=7)
                            else:
                                continue
                                
                            t["target_time"] = next_dt.strftime("%Y-%m-%d %H:%M:%S")
                            pending_tasks.append(t)
                    else:

                        pending_tasks.append(t)
                except Exception:

                    pass


            if triggered_tasks:
                try:
                    with open(TASKS_FILE, "w", encoding="utf-8") as f:
                        json.dump(pending_tasks, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

        for t in triggered_tasks:
            system_msg = (
                f"【系统内部心跳触发】\n"
                f"你设定的定时任务已到期，请立即主动提醒用户或执行动作。\n"
                f"任务内容：{t['description']}"
            )
            await task_queue.put(system_msg)