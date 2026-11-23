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
    # Prefer the real top-level window; generic class matches may pick
    # an invisible-to-reader child named merely "window" or "bibletime".
    title_pattern={"xiphos":r" - Xiphos$",
                   "bibletime":r"BibleTime [0-9]"}.get(app)
    if title_pattern:
        found=command(["xdotool","search","--onlyvisible","--name",title_pattern])
        candidates=[v for v in found.stdout.splitlines() if v.strip().isdigit()]
        for value in reversed(candidates):
            title=command(["xdotool","getwindowname",value]).stdout.strip()
            if title and ((" - Xiphos" in title) if app=="xiphos"
                          else title.casefold().startswith("bibletime ") and
                          any(ch.isdigit() for ch in title)):
                return value
    matches=[]
    for query in (["--class",app],["--name",app]):
        process=command(["xdotool","search","--onlyvisible",*query])
        values=[v for v in process.stdout.splitlines() if v.strip().isdigit()]
        for value in values:
            title=command(["xdotool","getwindowname",value]).stdout.strip().casefold()
            # Prefer the real application window to a transient child with
            # title "window", or the Xiphos locale prompt titled "Xiphos".
            if (app=="xiphos" and title.endswith(" - xiphos")) or (
                app=="bibletime" and title.startswith("bibletime ") and
                any(ch.isdigit() for ch in title)):
                return value
        matches.extend(values)
    return matches[-1] if matches else None

def named_window(pattern):
    proc=command(["xdotool","search","--onlyvisible","--name",pattern])
    matches=[x for x in proc.stdout.splitlines() if x.isdigit()]
    return matches[-1] if matches else None

def dismiss_dialog(pattern,key="Escape"):
    """Close known non-content startup dialog; never count it as article UI."""
    modal=named_window(pattern)
    if not modal:
        return False
    if command(["xdotool","windowactivate","--sync",modal],timeout=10).returncode:
        return False
    if command(["xdotool","key","--clearmodifiers",key],timeout=10).returncode:
        return False
    time.sleep(1)
    return not bool(named_window(pattern))

def dismiss_tip_of_day():
    """BibleTime may show a separate Tip of the Day after its Welcome screen."""
    if not named_window("Tip [Oo]f [Tt]he Day"):
        return False
    if dismiss_dialog("Tip [Oo]f [Tt]he Day"):
        return True
    modal=named_window("Tip [Oo]f [Tt]he Day")
    if not modal:
        return True
    # The standard Qt tip dialog has a "Close" control at bottom right.
    # Use its current window geometry rather than fixed screen coordinates.
    geometry=command(["xdotool","getwindowgeometry","--shell",modal],timeout=10)
    if geometry.returncode:
        return False
    values=dict(line.split("=",1) for line in geometry.stdout.splitlines()
                if "=" in line)
    width=int(values.get("WIDTH","0"))
    height=int(values.get("HEIGHT","0"))
    if width<100 or height<100:
        return False
    click=command(["xdotool","mousemove","--window",modal,
                   str(width-50),str(height-26)],timeout=10)
    if click.returncode or command(["xdotool","click","1"],timeout=10).returncode:
        return False
    time.sleep(1)
    return not bool(named_window("Tip [Oo]f [Tt]he Day"))

def window_origin(window):
    """Return desktop geometry origin for a real, visible GUI window."""
    result=command(["xdotool","getwindowgeometry","--shell",window],timeout=10)
    if result.returncode:
        raise RuntimeError("Unable to locate graphical reader window")
    values=dict(line.split("=",1) for line in result.stdout.splitlines()
                if "=" in line)
    return int(values["X"]),int(values["Y"])

def click_at(window,offset_x,offset_y,double=False):
    """Click a row relative to its containing *top-level* window."""
    x,y=window_origin(window)
    cmd=["xdotool","mousemove",str(x+offset_x),str(y+offset_y)]
    if command(cmd,timeout=10).returncode:
        raise RuntimeError("Unable to move pointer to reader control")
    click=["xdotool","click"]
    if double:
        click+=["--repeat","2","--delay","180"]
    click+=["1"]
    if command(click,timeout=10).returncode:
        raise RuntimeError("Unable to click reader control")

def test_reader(reader,outdir,lookup_key):
    name=reader["name"]
    log=outdir/(name+".log")
    env=os.environ.copy()
    env["GDK_BACKEND"]="x11"
    env["QT_QPA_PLATFORM"]="xcb"
    env["NO_AT_BRIDGE"]="1"
    if name=="xiphos":
        # Avoid a known locale-selection information dialog in headless CI.
        env["LANG"]="en_US.UTF-8"
        env["LC_ALL"]="en_US.UTF-8"
    # BibleTime 3.0.x may enumerate only system modules with SWORD_PATH.
    # Exercise its supported normal per-user ~/.sword installation instead.
    if name=="bibletime":
        env.pop("SWORD_PATH",None)
    with log.open("w",encoding="utf-8") as stream:
        process=subprocess.Popen(reader["argv"],env=env,
                                 stdout=stream,stderr=subprocess.STDOUT)
        window=None
        for _ in range(35):
            window=find_window(reader["window_class"])
            if window:
                title=command(["xdotool","getwindowname",window]).stdout.strip()
                if ((name=="xiphos" and title.endswith(" - Xiphos")) or
                    (name=="bibletime" and title.startswith("BibleTime "))):
                    break
            if process.poll() is not None:
                window=None
                break
            window=None
            time.sleep(1)
        result={"name":name,"executable":reader["argv"][0],
                "window_found":bool(window),"window_title":None,
                "screenshots":[],"startup_exit_status":process.poll(),
                "sword_install_source":"user_home" if name=="bibletime" else "SWORD_PATH",
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
            if name=="xiphos":
                # A locale information popup can consume the first dictionary
                # lookup keypress; dismiss it before Alt+D is sent.
                result["locale_notice_dismissed"]=dismiss_dialog("^Xiphos$",key="Return")
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
                result["tip_of_day_dismissed"]=dismiss_tip_of_day()
                time.sleep(2)
            shot=outdir/(name+"-startup.png")
            screen=command(["scrot",str(shot)],timeout=15)
            if screen.returncode==0 and shot.stat().st_size>1000:
                result["screenshots"].append(shot.name)
            if name=="xiphos":
                # Xiphos' documented Alt+D focuses dictionary navbar,
                # which is meaningful only if the module is selected in UI.
                # Send an actual representative lookup; screenshot is for
                # human review, not proof that a key displayed correctly.
                # Focus the visible dictionary lookup field; Alt+D alone
                # may target a different pane on a fresh Xiphos profile.
                click_at(window,545,380)
                command(["xdotool","key","--clearmodifiers","ctrl+a"],timeout=10)
                command(["xdotool","type","--clearmodifiers","--delay","80",lookup_key],timeout=10)
                command(["xdotool","key","Return"],timeout=10)
                time.sleep(2)
                result["post_lookup_locale_notice_dismissed"]=dismiss_dialog(
                    "^Xiphos$",key="Return"
                )
                time.sleep(1)
                shot=outdir/"xiphos-lookup-attempt.png"
                screen=command(["scrot",str(shot)],timeout=15)
                if screen.returncode==0 and shot.stat().st_size>1000:
                    result["screenshots"].append(shot.name)
            if name=="bibletime":
                # Exercise each visible bookshelf level before opening a
                # dictionary. Use *window-relative* GUI coordinates on this
                # fixed Xvfb fixture rather than absolute screen pixels.
                click_at(window,100,158)   # Lexicons and Dictionaries
                time.sleep(1)
                click_at(window,40,176)    # English language group
                time.sleep(1)
                expanded=outdir/"bibletime-lexicons-expanded.png"
                pic=command(["scrot",str(expanded)],timeout=15)
                if pic.returncode==0 and expanded.stat().st_size>1000:
                    result["screenshots"].append(expanded.name)
                click_at(window,115,195,double=True)   # module name
                time.sleep(3)
                opened=outdir/"bibletime-article-attempt.png"
                pic=command(["scrot",str(opened)],timeout=15)
                if pic.returncode==0 and opened.stat().st_size>1000:
                    result["screenshots"].append(opened.name)
                result["article_open_attempted_not_certified"]=True
            if name=="xiphos":
                result["blocking_first_run_dialog"]=bool(
                    named_window("Welcome to Xiphos") or
                    named_window("Module Manager") or
                    named_window("can not create directory") or
                    named_window("^Xiphos$")
                )
            else:
                result["blocking_first_run_dialog"]=bool(
                    named_window("Welcome to BibleTime") or
                    named_window("Tip [Oo]f [Tt]he Day")
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
    parser.add_argument("--lookup-key",required=True)
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
    readers=[test_reader(r,out,args.lookup_key) for r in READERS]
    report={
       "schema_version":1,"module":args.module_id,"lookup_key":args.lookup_key,
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
        raise SystemExit("GUI reader blocked by a startup/modal dialog: not an acceptance test")
    required={"xiphos":{"xiphos-startup.png","xiphos-lookup-attempt.png"},
              "bibletime":{"bibletime-startup.png",
                           "bibletime-lexicons-expanded.png",
                           "bibletime-article-attempt.png"}}
    for reader in readers:
        if not required[reader["name"]].issubset(set(reader["screenshots"])):
            raise SystemExit("Missing readable GUI screenshot for "+reader["name"])

if __name__=="__main__":
    main()
