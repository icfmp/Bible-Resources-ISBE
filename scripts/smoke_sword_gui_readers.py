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

def click_at_origin(origin,offset_x,offset_y,double=False):
    """Click at a known desktop origin, even after Qt recreates a window."""
    x,y=origin
    cmd=["xdotool","mousemove",str(x+offset_x),str(y+offset_y)]
    if command(cmd,timeout=10).returncode:
        raise RuntimeError("Unable to move pointer to reader control")
    click=["xdotool","click"]
    if double:
        click+=["--repeat","2","--delay","180"]
    click+=["1"]
    if command(click,timeout=10).returncode:
        raise RuntimeError("Unable to click reader control")

def click_at(window,offset_x,offset_y,double=False):
    """Click a widget relative to the currently valid top-level window."""
    return click_at_origin(window_origin(window),offset_x,offset_y,double)

def attempt_scripture_link(reader_name, outdir, result):
    """Send a real pointer click to an observed link in the fixed Xvfb fixture.

    This is a diagnostic interaction, NOT an assertion that the displayed
    destination is correct. A separate human review of the resulting PNG must
    explicitly determine whether navigation occurred. The positions were
    calibrated against the preserved AARON lookup screenshots in this *exact*
    1440x900/1200x760 GitHub Actions reader fixture (not arbitrary desktops).
    If the layouts change, the evidence must be recalibrated, not rubber-stamped.
    """
    if reader_name == "bibletime":
        # Blue "Ex 6:20" in the first AARON paragraph. Actual screenshot:
        # https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45280079561
        screen_xy = (476, 239)
    elif reader_name == "xiphos":
        # Grey "Ex 6:20" in first visible AARON paragraph of Book View.
        # https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45279693011
        screen_xy = (943, 703)
    else:
        raise ValueError(f"Unknown GUI reader: {reader_name}")
    before = command(["xdotool", "getactivewindow", "getwindowname"], timeout=10)
    probe = {
        "source_article_key": "AARON",
        "source_reference_label": "Ex 6:20",
        "probe_screen_coordinates": list(screen_xy),
        "coordinate_scope": "pinned Xvfb screenshot fixture only",
        "window_title_before": before.stdout.strip(),
        "click_command_succeeded": False,
        "window_title_after": None,
        "screenshot": None,
        "click_destination_verified": False,
        "requires_independent_visual_review": True,
    }
    filename = outdir / (reader_name + "-scripture-click-attempt.png")
    try:
        # xdotool takes *screen* coordinates; do not use stale Qt client
        # origins after opening BibleTime's separate document window.
        move = command(["xdotool", "mousemove", str(screen_xy[0]), str(screen_xy[1])], timeout=10)
        click = command(["xdotool", "click", "1"], timeout=10) if move.returncode == 0 else move
        probe["click_command_succeeded"] = move.returncode == 0 and click.returncode == 0
        time.sleep(3)
        after = command(["xdotool", "getactivewindow", "getwindowname"], timeout=10)
        probe["window_title_after"] = after.stdout.strip()
        captured = command(["scrot", str(filename)], timeout=15)
        if captured.returncode == 0 and filename.is_file() and filename.stat().st_size > 1000:
            probe["screenshot"] = filename.name
            result["screenshots"].append(filename.name)
    except (subprocess.TimeoutExpired, OSError) as exc:
        probe["diagnostic_error"] = str(exc)
    if reader_name == "bibletime" and probe["click_command_succeeded"]:
        # The first captured BibleTime state can show a newly opened Bible
        # pane with the requested *title* but a previous Genesis 1 body.
        # Record a separate settled view before assessing verse display.
        time.sleep(8)
        settled = outdir / "bibletime-scripture-click-settled.png"
        resultshot = command(["scrot", str(settled)], timeout=15)
        if resultshot.returncode == 0 and settled.is_file() and settled.stat().st_size > 1000:
            probe["settled_screenshot"] = settled.name
            result["screenshots"].append(settled.name)
        probe["settled_window_title"] = command(
            ["xdotool", "getactivewindow", "getwindowname"], timeout=10
        ).stdout.strip()
    result["scripture_link_click_probe"] = probe
    return probe

def test_reader(reader,outdir,lookup_key,internal_link_key=None,click_fixture=None):
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
            # xdotool geometry reports the client origin (below decorations);
            # document the actual origin for repeatable click diagnostics.
            result["window_client_origin"]=list(window_origin(window))
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
                click_at(window,820,420)
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
                click_at(window,10,119)   # expand Lexicons via disclosure arrow
                time.sleep(1)
                click_at(window,30,138)   # expand English via disclosure arrow
                time.sleep(1)
                expanded=outdir/"bibletime-lexicons-expanded.png"
                pic=command(["scrot",str(expanded)],timeout=15)
                if pic.returncode==0 and expanded.stat().st_size>1000:
                    result["screenshots"].append(expanded.name)
                click_at(window,115,157,double=True)   # module name
                time.sleep(3)
                opened=outdir/"bibletime-article-attempt.png"
                pic=command(["scrot",str(opened)],timeout=15)
                if pic.returncode==0 and opened.stat().st_size>1000:
                    result["screenshots"].append(opened.name)
                result["article_open_attempted_not_certified"]=True
                # Once the module's initial index opens, use its own entry
                # lookup box to request the explicit headword being audited.
                # BibleTime may reparent/destroy its original top-level X11
                # window when opening the lexicon document. The screen stays
                # fixed, so use its previously recorded client origin.
                click_at_origin(result["window_client_origin"],405,80)
                command(["xdotool","key","--clearmodifiers","ctrl+a"],timeout=10)
                command(["xdotool","type","--clearmodifiers","--delay","70",lookup_key],timeout=10)
                command(["xdotool","key","Return"],timeout=10)
                time.sleep(3)
                lookupshot=outdir/"bibletime-lookup-attempt.png"
                pic=command(["scrot",str(lookupshot)],timeout=15)
                if pic.returncode==0 and lookupshot.stat().st_size>1000:
                    result["screenshots"].append(lookupshot.name)
                result["headword_lookup_attempted_not_certified"]=True
            if internal_link_key:
                # Take a separate actual on-screen lookup of a dictionary
                # article with an original source-attested early internal link.
                # It remains a diagnostic, NOT a certified clickable link.
                if name=="xiphos":
                    click_at(window,820,420)
                else:
                    click_at_origin(result["window_client_origin"],405,80)
                command(["xdotool","key","--clearmodifiers","ctrl+a"],timeout=10)
                command(["xdotool","type","--clearmodifiers","--delay","65",internal_link_key],timeout=10)
                command(["xdotool","key","Return"],timeout=10)
                time.sleep(3)
                candidate_image=outdir/(name+"-internal-link-source.png")
                image=command(["scrot",str(candidate_image)],timeout=15)
                if image.returncode==0 and candidate_image.is_file() and candidate_image.stat().st_size>1000:
                    result["screenshots"].append(candidate_image.name)
                result["internal_link_source_lookup"]={
                    "source_article":internal_link_key,
                    "screenshot":candidate_image.name if candidate_image.is_file() else None,
                    "article_to_article_click_verified":False,
                    "requires_source_link_coordinate_review":True
                }
                if click_fixture is not None:
                    # These coordinates were reviewed in actual screenshots
                    # from this exact Xvfb fixture, NOT inferred from TEI.
                    spot=click_fixture["coordinates"][name]
                    x,y=spot["x"],spot["y"]
                    previous=command(["xdotool","getactivewindow","getwindowname"],timeout=10)
                    moved=command(["xdotool","mousemove",str(x),str(y)],timeout=10)
                    clicked=command(["xdotool","click","1"],timeout=10) if moved.returncode==0 else moved
                    time.sleep(4)
                    clickshot=outdir/(name+"-internal-link-click-attempt.png")
                    grabbed=command(["scrot",str(clickshot)],timeout=15)
                    if grabbed.returncode==0 and clickshot.is_file() and clickshot.stat().st_size>1000:
                        result["screenshots"].append(clickshot.name)
                    after=command(["xdotool","getactivewindow","getwindowname"],timeout=10)
                    result["internal_article_link_click_probe"]={
                        "source_article":internal_link_key,
                        "expected_destination":click_fixture["destination_article"],
                        "link_text":click_fixture["original_link_text"],
                        "observed_screen_click_point":[x,y],
                        "screen_geometry":"1440x900 Xvfb fixture only",
                        "click_command_succeeded":moved.returncode==0 and clicked.returncode==0,
                        "before_window_title":previous.stdout.strip(),
                        "after_window_title":after.stdout.strip(),
                        "post_click_screenshot":clickshot.name if clickshot.is_file() else None,
                        "destination_article_body_verified":False,
                        "requires_independent_visual_review":True
                    }
                # Restore AARON so existing observed Scripture reference
                # coordinates are still valid. Do NOT assume that navigating
                # to the candidate changed/retained the same screen layout.
                if name=="xiphos":
                    click_at(window,820,420)
                else:
                    click_at_origin(result["window_client_origin"],405,80)
                command(["xdotool","key","--clearmodifiers","ctrl+a"],timeout=10)
                command(["xdotool","type","--clearmodifiers","--delay","65",lookup_key],timeout=10)
                command(["xdotool","key","Return"],timeout=10)
                time.sleep(3)
                restored=outdir/(name+"-restored-before-scripture.png")
                image=command(["scrot",str(restored)],timeout=15)
                if image.returncode==0 and restored.is_file() and restored.stat().st_size>1000:
                    result["screenshots"].append(restored.name)
            # Diagnostic only: actual pointer event and post-click screenshot.
            # Never infer navigation correctness from process exit or PNG size.
            attempt_scripture_link(name,outdir,result)
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
    parser.add_argument("--internal-link-key",default=None,
                        help="Source article containing an early internal link")
    parser.add_argument("--internal-link-click-fixture",default=None,
                        help="Pinned actual screen coordinates grounded in GUI screenshots")
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
    click_fixture=None
    if args.internal_link_click_fixture:
        if not args.internal_link_key:
            raise SystemExit("Internal click fixture requires --internal-link-key")
        click_fixture=json.loads(Path(args.internal_link_click_fixture).read_text(encoding="utf-8"))
        if (click_fixture.get("schema_version")!=1 or
            click_fixture.get("source_article")!=args.internal_link_key or
            set(click_fixture.get("coordinates",{}))!={r["name"] for r in READERS}):
            raise SystemExit("Internal link click fixture does not match active source/reader inventory")
        for reader in READERS:
            point=click_fixture["coordinates"][reader["name"]]
            if not (0<=point["x"]<1440 and 0<=point["y"]<900):
                raise SystemExit("Invalid pinned Xvfb point for "+reader["name"])
    readers=[test_reader(r,out,args.lookup_key,args.internal_link_key,click_fixture) for r in READERS]
    report={
       "schema_version":1,"module":args.module_id,"lookup_key":args.lookup_key,
       "internal_link_candidate_lookup_key":args.internal_link_key,
       "interactive_dictionary_to_dictionary_link_verified":False,
       "internal_encyclopedia_link_click_attempted_in_both_readers":bool(click_fixture),
       "scope":"visible_GUI_launch_headword_lookup_and_scripture_pointer_probe",
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
                           "bibletime-article-attempt.png",
                           "bibletime-lookup-attempt.png"}}
    for reader in readers:
        if not required[reader["name"]].issubset(set(reader["screenshots"])):
            raise SystemExit("Missing readable GUI screenshot for "+reader["name"])
    for reader in readers:
        probe = reader.get("scripture_link_click_probe", {})
        # Strictly assert a real UI event and screenshot were produced, but
        # NOT that an unknown destination navigation magically passed.
        if not probe.get("click_command_succeeded") or not probe.get("screenshot"):
            raise SystemExit("Missing attempted GUI reference click evidence for "+reader["name"])
    if args.internal_link_key:
        for reader in readers:
            source_probe=reader.get("internal_link_source_lookup",{})
            if source_probe.get("source_article")!=args.internal_link_key or not source_probe.get("screenshot"):
                raise SystemExit("Missing internal article-link source screenshot for "+reader["name"])
            if reader["name"]+"-restored-before-scripture.png" not in reader["screenshots"]:
                raise SystemExit("Missing restored original source lookup for "+reader["name"])
            if click_fixture is not None:
                probe=reader.get("internal_article_link_click_probe",{})
                if not probe.get("click_command_succeeded") or not probe.get("post_click_screenshot"):
                    raise SystemExit("Missing real encyclopedia-reference click evidence for "+reader["name"])
    for reader in readers:
        if reader["name"] == "bibletime":
            probe = reader.get("scripture_link_click_probe", {})
            if "choose standard bible" in probe.get("window_title_after", "").casefold():
                raise SystemExit("BibleTime has no configured standard Bible for source reference navigation")
            if not probe.get("settled_screenshot"):
                raise SystemExit("BibleTime post-click settled-view screenshot missing")

if __name__=="__main__":
    main()
