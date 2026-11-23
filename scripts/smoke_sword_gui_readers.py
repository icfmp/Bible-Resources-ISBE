#!/usr/bin/env python3
"""Headless installed-module smoke for independent Xiphos and BibleTime UIs.

Only asserts that a real visible GUI opens with the separately compiled SWORD
module installed. It does NOT certify correct rendering or link-click behavior.
Screenshots and app diagnostic logs enable a separately documented visual audit.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

READERS=[
    {"name":"xiphos","argv":["xiphos"],"window_class":"xiphos"},
    {"name":"bibletime","argv":["bibletime","--ignore-session"],"window_class":"bibletime"},
]

def command(args,**kw):
    return subprocess.run(args,capture_output=True,text=True,**kw)

def find_window(app):
    for query in (["--class",app],["--name",app]):
        process=command(["xdotool","search","--onlyvisible",*query])
        values=[v for v in process.stdout.splitlines() if v.strip().isdigit()]
        if values:
            return values[-1]
    return None

def named_window(pattern):
    proc=command(["xdotool","search","--onlyvisible","--name",pattern])
    matches=[x for x in proc.stdout.splitlines() if x.isdigit()]
    return matches[-1] if matches else None

def test_reader(reader,outdir):
    name=reader["name"]
    log=outdir/(name+".log")
    env=os.environ.copy()
    env["GDK_BACKEND"]="x11"
    env["QT_QPA_PLATFORM"]="xcb"
    env["NO_AT_BRIDGE"]="1"
    with log.open("w",encoding="utf-8") as stream:
        process=subprocess.Popen(reader["argv"],env=env,
                                 stdout=stream,stderr=subprocess.STDOUT)
        window=None
        for _ in range(35):
            window=find_window(reader["window_class"])
            if window:
                break
            if process.poll() is not None:
                break
            time.sleep(1)
        result={"name":name,"executable":reader["argv"][0],
                "window_found":bool(window),"window_title":None,
                "screenshots":[],"startup_exit_status":process.poll(),
                "module_name_visible_in_window_unverified":True,
                "article_markup_visible_unverified":True,
                "gui_link_click_unverified":True}
        try:
            if not window:
                return result
            title=command(["xdotool","getwindowname",window])
            result["window_title"]=title.stdout.strip()
            command(["xdotool","windowactivate","--sync",window],timeout=10)
            command(["xdotool","windowsize",window,"1200","760"],timeout=10)
            command(["xdotool","windowmove",window,"0","0"],timeout=10)
            time.sleep(2)
            if name=="bibletime":
                # BibleTime's fresh profile displays a welcome modal even
                # with a separately valid local dictionary installation.
                # Dismiss "Install later" without downloading anything.
                modal=named_window("Welcome to BibleTime")
                if modal:
                    command(["xdotool","windowactivate","--sync",modal],timeout=10)
                    command(["xdotool","mousemove","--window",modal,"500","296"],timeout=10)
                    command(["xdotool","click","1"],timeout=10)
                    result["fresh_profile_welcome_dismissed"]=True
                    time.sleep(4)
                else:
                    result["fresh_profile_welcome_dismissed"]=False
            shot=outdir/(name+"-startup.png")
            screen=command(["scrot",str(shot)],timeout=15)
            if screen.returncode==0 and shot.stat().st_size>1000:
                result["screenshots"].append(shot.name)
            if name=="xiphos":
                # Xiphos' documented Alt+D focuses dictionary navbar,
                # which is meaningful only if the module is selected in UI.
                # Send an actual representative lookup; screenshot is for
                # human review, not proof that a key displayed correctly.
                command(["xdotool","key","--clearmodifiers","alt+d"],timeout=10)
                command(["xdotool","type","--clearmodifiers","--delay","80","AARON"],timeout=10)
                command(["xdotool","key","Return"],timeout=10)
                time.sleep(3)
                shot=outdir/"xiphos-aaron-attempt.png"
                screen=command(["scrot",str(shot)],timeout=15)
                if screen.returncode==0 and shot.stat().st_size>1000:
                    result["screenshots"].append(shot.name)
            if name=="xiphos":
                result["blocking_first_run_dialog"]=bool(
                    named_window("Welcome to Xiphos") or
                    named_window("Module Manager") or
                    named_window("can not create directory")
                )
            else:
                result["blocking_first_run_dialog"]=bool(
                    named_window("Welcome to BibleTime")
                )
            return result
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True)
    parser.add_argument("--module-id",required=True)
    args=parser.parse_args()
    if not os.getenv("DISPLAY") or not os.getenv("SWORD_PATH"):
        raise SystemExit("Require active X display and isolated SWORD_PATH")
    for package in ("xdotool","scrot","xiphos","bibletime","diatheke"):
        if not shutil.which(package):
            raise SystemExit("Missing independent reader tool: "+package)
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    # Prevent the previous false positive: an error dialog alone is not
    # evidence of a successfully initialized reader. Its writable parent
    # paths must exist before the apps start.
    for name in ("XDG_DATA_HOME","XDG_CONFIG_HOME","XDG_CACHE_HOME"):
        base=Path(os.environ.get(name,""))
        if not base.is_dir() or not os.access(base,os.W_OK):
            raise SystemExit(f"Reader XDG storage is not writable: {name}")
    # Verify libSWORD itself sees our precise candidate install root.
    lookup=command(["diatheke","-b","system","-k","modulelist"])
    if lookup.returncode or args.module_id not in lookup.stdout:
        raise SystemExit("Native corrected SWORD module not discoverable")
    readers=[test_reader(r,out) for r in READERS]
    report={
       "schema_version":1,"module":args.module_id,
       "scope":"visible_GUI_launch_only_plus_keyboard_navigation_attempt",
       "independent_gui_readers":readers,
       "visible_reader_window_count":sum(bool(r["window_found"]) for r in readers),
       "blocking_first_run_dialogs":sum(bool(r.get("blocking_first_run_dialog")) for r in readers),
       "extra_bible_test_fixture":"Ubuntu sword-text-kjv, independent of curated ISBE payload",
       "interactive_hyperlink_click_tested":False,
       "article_body_rendering_certified":False,
       "rights_cleared":False,"publication_approved":False
    }
    (out/"GUI_SMOKE.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if report["visible_reader_window_count"]!=len(readers):
        raise SystemExit("One or more graphical readers did not open")
    if report["blocking_first_run_dialogs"]:
        raise SystemExit("GUI reader blocked by welcome/module-manager/error dialog: not an acceptance test")

if __name__=="__main__":
    main()
