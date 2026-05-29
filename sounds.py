"""
sounds.py — procedural sound generation.
Call init() once after pygame.init(), then use play(key) anywhere.
"""
import array
import math
import os
import ssl
import urllib.request
import random as _rnd
import pygame

SOUNDS: dict = {}
_R = 44100   # sample rate

MUSIC_DIR = os.path.join(os.path.dirname(__file__), "assets", "music")

# Each entry: (filename, [url_primary, url_fallback, ...])
# Kevin MacLeod CC-BY 4.0 — incompetech.com / archive.org mirror
_MUSIC_TRACKS = [
    ("biome_0.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Killers.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Spellbound.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Hitman.mp3",
    ]),
    ("biome_1.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Hitman.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Hitman.mp3",
    ]),
    ("biome_2.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Tense_Times.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Tense%20Times.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3",
    ]),
    ("biome_3.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile_Reaction.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Volatile_Reaction.mp3",
    ]),
    ("biome_4.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest_Child.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Darkest_Child.mp3",
    ]),
    ("biome_5.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Clash_Defiant.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Clash%20Defiant.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Clash_Defiant.mp3",
    ]),
    ("biome_6.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact_Moderato.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact%20Moderato.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Impact_Moderato.mp3",
    ]),
    # ── Run 2 biome tracks ────────────────────────────────────────────────────
    ("biome_7.mp3",  [   # Space
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile_Reaction.mp3",
    ]),
    ("biome_8.mp3",  [   # Ocean
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact%20Moderato.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact_Moderato.mp3",
    ]),
    ("biome_9.mp3",  [   # Crystal Cave
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest_Child.mp3",
    ]),
    ("biome_10.mp3", [   # Infernal
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Clash%20Defiant.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Clash_Defiant.mp3",
    ]),
    ("biome_11.mp3", [   # Mushroom
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Hitman.mp3",
    ]),
    ("biome_12.mp3", [   # Storm Tundra
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile_Reaction.mp3",
    ]),
    ("biome_13.mp3", [   # Hellscape
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact%20Moderato.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Impact_Moderato.mp3",
    ]),
    ("lobby.mp3", [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dewdrop_Fantasy.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dewdrop%20Fantasy.mp3",
        "https://archive.org/download/Kevin_MacLeod_Discography/Dewdrop_Fantasy.mp3",
    ]),
]

# SSL context that skips verification (fixes Windows certificate errors)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode    = ssl.CERT_NONE

_MP3_MAGIC = (b'ID3', b'\xff\xfb', b'\xff\xfa', b'\xff\xf3', b'\xff\xf2')

def _valid_mp3(path):
    """Return True if the file starts with MP3/ID3 magic bytes."""
    try:
        with open(path, 'rb') as f:
            h = f.read(3)
        return any(h.startswith(m) for m in _MP3_MAGIC)
    except Exception:
        return False

def _fetch_music():
    """Download any missing or corrupt music files on startup."""
    os.makedirs(MUSIC_DIR, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    for fname, urls in _MUSIC_TRACKS:
        path = os.path.join(MUSIC_DIR, fname)
        if os.path.exists(path) and _valid_mp3(path):
            continue                          # already good
        if os.path.exists(path):
            os.remove(path)                   # corrupt — delete and retry
        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=20,
                                            context=_SSL_CTX) as r:
                    data = r.read()
                if len(data) > 5000 and any(data[:3].startswith(m)
                                             for m in _MP3_MAGIC):
                    with open(path, 'wb') as f:
                        f.write(data)
                    print(f"[music] downloaded {fname}")
                    break
            except Exception:
                pass
        else:
            print(f"[music] all URLs failed for {fname} — no music on this level")


def _buf(samples):
    """Convert float list → stereo pygame Sound."""
    out = []
    for s in samples:
        v = max(-32767, min(32767, int(s)))
        out.extend([v, v])          # duplicate for stereo
    return pygame.mixer.Sound(buffer=array.array('h', out))


def _s(t, freq, amp=1.0):          # sine helper
    return amp * math.sin(2 * math.pi * freq * t)


def _exp(t, rate):                  # exponential decay helper
    return math.exp(-rate * t)


def init():
    _fetch_music()          # download missing tracks (skips existing files)
    if not pygame.mixer.get_init():
        pygame.mixer.init(_R, -16, 2, 512)

    rng = _rnd.Random(7)

    def noise():
        return rng.uniform(-1.0, 1.0)

    # ── Jump ─────────────────────────────────────────────────────────────────
    def _jump():
        dur, n = 0.13, int(_R * 0.13)
        return _buf([_s(i/_R, 180 + 380*(i/_R/dur), 0.30) * _exp(i/_R, 16)
                     * 32767 for i in range(n)])

    # ── Pistol ───────────────────────────────────────────────────────────────
    def _pistol():
        n = int(_R * 0.07)
        return _buf([(_s(i/_R, 900, .55) + _s(i/_R, 1800, .25) + noise()*.2)
                     * _exp(i/_R, 55) * 0.40 * 32767 for i in range(n)])

    # ── Blaster ──────────────────────────────────────────────────────────────
    def _blaster():
        dur, n = 0.15, int(_R * 0.15)
        return _buf([(_s(i/_R, 620 - 300*(i/_R/dur), .70)
                      + _s(i/_R, 1240 - 600*(i/_R/dur), .20) + noise()*.10)
                     * _exp(i/_R, 20) * 0.45 * 32767 for i in range(n)])

    # ── Rifle ────────────────────────────────────────────────────────────────
    def _rifle():
        n = int(_R * 0.055)
        return _buf([(_s(i/_R, 1300, .45) + noise()*.55)
                     * _exp(i/_R, 80) * 0.45 * 32767 for i in range(n)])

    # ── Shotgun ──────────────────────────────────────────────────────────────
    def _shotgun():
        n = int(_R * 0.20)
        return _buf([(noise()*.55 + _s(i/_R, 110, .30) + _s(i/_R, 280, .15))
                     * _exp(i/_R, 13) * 0.65 * 32767 for i in range(n)])

    # ── Grenade throw ────────────────────────────────────────────────────────
    def _throw():
        dur, n = 0.09, int(_R * 0.09)
        return _buf([(_s(i/_R, 380 + 220*(i/_R/dur), .60) + noise()*.40)
                     * _exp(i/_R, 28) * 0.22 * 32767 for i in range(n)])

    # ── Explosion ────────────────────────────────────────────────────────────
    def _explosion():
        n = int(_R * 0.50)
        return _buf([(noise()*.65 + _s(i/_R, 72, .22) + _s(i/_R, 145, .13))
                     * _exp(i/_R, 7) * 0.82 * 32767 for i in range(n)])

    # ── Player hit ───────────────────────────────────────────────────────────
    def _player_hit():
        dur, n = 0.14, int(_R * 0.14)
        return _buf([(_s(i/_R, 340 - 160*(i/_R/dur), .70) + noise()*.30)
                     * _exp(i/_R, 20) * 0.42 * 32767 for i in range(n)])

    # ── Enemy hit ────────────────────────────────────────────────────────────
    def _enemy_hit():
        n = int(_R * 0.055)
        return _buf([(_s(i/_R, 580, .80) + noise()*.20)
                     * _exp(i/_R, 55) * 0.28 * 32767 for i in range(n)])

    # ── Enemy death ──────────────────────────────────────────────────────────
    def _enemy_death():
        dur, n = 0.22, int(_R * 0.22)
        return _buf([(_s(i/_R, 480 - 300*(i/_R/dur), .70) + noise()*.30)
                     * _exp(i/_R, 11) * 0.38 * 32767 for i in range(n)])

    # ── Weapon pickup ────────────────────────────────────────────────────────
    def _pickup_weapon():
        n = int(_R * 0.17)
        return _buf([(_s(i/_R, 600, .45) + _s(i/_R, 900, .30) + _s(i/_R, 1200, .25))
                     * (1 - i/_R/0.17) * 0.32 * 32767 for i in range(n)])

    # ── Biome item pickup ─────────────────────────────────────────────────────
    def _pickup_item():
        n = int(_R * 0.32)
        freqs = [440, 554, 659, 880]
        return _buf([sum(_s(i/_R, f*(1+.015*j), .25) for j, f in enumerate(freqs))
                     * (1 - i/_R/0.32) * 0.38 * 32767 for i in range(n)])

    # ── Health pickup ─────────────────────────────────────────────────────────
    def _pickup_health():
        n = int(_R * 0.18)
        return _buf([(_s(i/_R, 440, .50) + _s(i/_R, 660, .50))
                     * (1 - i/_R/0.18) * 0.28 * 32767 for i in range(n)])

    # ── Portal opens ─────────────────────────────────────────────────────────
    def _portal_open():
        dur, n = 0.55, int(_R * 0.55)
        return _buf([(_s(i/_R, 200 + 320*(i/_R/dur), .55)
                      + _s(i/_R, (200+320*(i/_R/dur))*1.5, .30)
                      + noise()*.05)
                     * min(i/_R*5, 1) * (1 - i/_R/dur) * 0.28 * 32767
                     for i in range(n)])

    # ── Coin ─────────────────────────────────────────────────────────────────
    def _coin():
        n = int(_R * 0.09)
        return _buf([(_s(i/_R, 1047, .60) + _s(i/_R, 1319, .40))
                     * _exp(i/_R, 32) * 0.28 * 32767 for i in range(n)])

    # ── Game over ─────────────────────────────────────────────────────────────
    def _game_over():
        dur, n = 0.65, int(_R * 0.65)
        return _buf([(_s(i/_R, 300 - 210*(i/_R/dur), .60)
                      + _s(i/_R, (300-210*(i/_R/dur))*.75, .40))
                     * (1 - i/_R/dur) * 0.40 * 32767 for i in range(n)])

    # ── Level complete (short fanfare) ────────────────────────────────────────
    def _level_complete():
        notes = [(392, 0.10), (523, 0.10), (659, 0.10), (784, 0.20)]
        all_s = []
        for freq, dur in notes:
            n = int(_R * dur)
            all_s.extend([(_s(i/_R, freq, .60) + _s(i/_R, freq*2, .20))
                           * (1 - i/_R/dur) * 0.32 * 32767 for i in range(n)])
        return _buf(all_s)

    # ── Cinematic orchestral music generator ────────────────────────────────
    def _cin(bpm, bass4, chord4, perc, mel, ost=None, mamp=0.22):
        """
        bpm    – tempo
        bass4  – 4 bass root frequencies (low brass)
        chord4 – 4 chord frequency lists (strings + brass pads)
        perc   – list of (type, abs_beat): type in 'kick','snare','hat','hat2'
        mel    – list of (freq, abs_beat, dur_beats)  — brass lead melody
        """
        B = 60 / bpm
        n = int(_R * 16 * B)
        m = [0.0] * n

        def T(ab): return ab * B

        # Brass / horn — harmonic series, fast attack
        def brass(t0, dur, freq, amp, dc=4.0):
            s, e = int(t0*_R), min(n, int((t0+dur)*_R))
            for i in range(s, e):
                t   = (i-s)/_R
                atk = min(t * 35, 1.0)
                env = amp * atk * math.exp(-dc * t)
                m[i] += env * (
                    1.00 * math.sin(2*math.pi*freq*t) +
                    0.52 * math.sin(2*math.pi*2*freq*t) +
                    0.30 * math.sin(2*math.pi*3*freq*t) +
                    0.18 * math.sin(2*math.pi*4*freq*t) +
                    0.10 * math.sin(2*math.pi*5*freq*t) +
                    0.06 * math.sin(2*math.pi*6*freq*t))

        # Tremolo strings — slow attack, amplitude modulated
        def strings(t0, dur, freq, amp, dc=0.7):
            s, e = int(t0*_R), min(n, int((t0+dur)*_R))
            for i in range(s, e):
                t   = (i-s)/_R
                atk = min(t * 5, 1.0)
                env = amp * atk * math.exp(-dc * t)
                trem = 0.76 + 0.24 * math.sin(2*math.pi*7.5*t)
                m[i] += env * trem * (
                    math.sin(2*math.pi*freq*t) +
                    0.28 * math.sin(2*math.pi*freq*1.007*t))

        # Timpani — pitched drum with natural pitch decay
        def timpani(t0, freq, amp):
            s, e = int(t0*_R), min(n, int((t0+1.8)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                env = amp * math.exp(-t * 5)
                f   = freq * math.exp(-t * 0.7)
                m[i] += env * (
                    0.80 * math.sin(2*math.pi*f*t) +
                    0.15 * math.sin(2*math.pi*f*2.74*t) +
                    0.05 * rng.uniform(-1,1) * math.exp(-t*20))

        # Orchestral snare
        def orch_snare(t0, amp):
            s, e = int(t0*_R), min(n, int((t0+0.28)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                m[i] += amp * (
                    0.55 * rng.uniform(-1,1) * math.exp(-t*22) +
                    0.30 * math.sin(2*math.pi*195*t) * math.exp(-t*18) +
                    0.15 * math.sin(2*math.pi*320*t) * math.exp(-t*26))

        # Crash cymbal — big moment marker
        def crash(t0, amp=0.22):
            s, e = int(t0*_R), min(n, int((t0+1.2)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                m[i] += amp * rng.uniform(-1,1) * math.exp(-t*4)

        # Staccato strings ostinato — the Marvel "engine"
        def staccato(t0, dur_beats, freq, amp):
            step = B * 0.5   # 8th-note spacing
            note_len = step * 0.55
            dc = 14          # fast decay = staccato bowing
            t = t0
            end = t0 + dur_beats * B
            while t < end - step * 0.5:
                s, e = int(t*_R), min(n, int((t+note_len)*_R))
                for i in range(s, e):
                    ti = (i-s)/_R
                    atk = min(ti*60, 1.0)
                    env = amp * atk * math.exp(-dc*ti)
                    trem = 0.8 + 0.2*math.sin(2*math.pi*8*ti)
                    m[i] += env * trem * math.sin(2*math.pi*freq*ti)
                t += step

        # Hip-hop kick — punchy pitch-drop thud (Pemberton sub hit)
        def hkick(t0, amp=0.94):
            s, e = int(t0*_R), min(n, int((t0+0.35)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                f = 88 * math.exp(-t * 16)
                m[i] += amp * math.exp(-t*9) * math.sin(2*math.pi*f*t)
                m[i] += amp * 0.22 * math.exp(-t*42) * rng.uniform(-1, 1)

        # Sub bass — deep 40–55 Hz rumble under the beat
        def sub(t0, dur, freq, amp=0.62):
            s, e = int(t0*_R), min(n, int((t0+dur)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                m[i] += amp * min(t*28, 1.) * math.exp(-t*2.2) * math.sin(2*math.pi*freq*t)

        # Industrial metal hit — King Arthur percussion
        def metal(t0, amp=0.54):
            s, e = int(t0*_R), min(n, int((t0+0.22)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                env = amp * math.exp(-t * 22)
                m[i] += env * (0.40*math.sin(2*math.pi*348*t) +
                               0.30*math.sin(2*math.pi*540*t) +
                               0.20*math.sin(2*math.pi*820*t) +
                               0.10*rng.uniform(-1, 1))

        # Clap — hip-hop snare alternative (Spider-Verse)
        def clap(t0, amp=0.50):
            s, e = int(t0*_R), min(n, int((t0+0.09)*_R))
            for i in range(s, e):
                t = (i-s)/_R
                m[i] += amp * rng.uniform(-1,1) * math.exp(-t*34) * (
                    1 + 0.5*math.sin(2*math.pi*195*t))

        # Cymbal / hi-hat
        def hat(t0, amp=0.07):
            s, e = int(t0*_R), min(n, int((t0+0.04)*_R))
            for i in range(s, min(e, n)):
                t = (i-s)/_R
                m[i] += amp * rng.uniform(-1,1) * math.exp(-t*75)

        # Percussion
        for ptype, ab in perc:
            t0 = T(ab)
            if   ptype == 'kick':   timpani(t0, 65, 0.90)
            elif ptype == 'hkick':  hkick(t0)
            elif ptype == 'snare':  orch_snare(t0, 0.58)
            elif ptype == 'clap':   clap(t0)
            elif ptype == 'hat':    hat(t0, 0.07)
            elif ptype == 'hat2':   hat(t0, 0.04)
            elif ptype == 'crash':  crash(t0, 0.22)
            elif ptype == 'metal':  metal(t0)

        # Staccato string ostinato
        if ost:
            for freq, ab, dur in ost:
                staccato(T(ab), dur, freq, 0.13)

        # Low brass bass + sub-bass doubling (octave below)
        for bar, root in enumerate(bass4):
            brass(T(bar*4),   B*1.9, root,       0.48, 3.0)
            sub(  T(bar*4),   B*1.8, root * 0.5, 0.60)    # one octave lower
            brass(T(bar*4+2), B*0.9, root,       0.36, 5.0)
            sub(  T(bar*4+2), B*0.8, root * 0.5, 0.32)
            brass(T(bar*4+3), B*0.9, root*1.33,  0.26, 6.0)

        # Strings pad + brass stab on bars 1 and 3
        for bar, freqs in enumerate(chord4):
            for f in freqs:
                strings(T(bar*4), B*3.85, f, 0.10, 0.6)
            if bar % 2 == 0:
                for f in freqs:
                    brass(T(bar*4), B*0.28, f, 0.14, 10)

        # Brass melody
        for freq, ab, dur in mel:
            brass(T(ab), B*dur*0.87, freq, mamp, 3.5)

        # Simulate room reverb with two short echo delays
        d1 = int(_R * 0.07)
        for i in range(d1, n): m[i] += m[i-d1] * 0.16
        d2 = int(_R * 0.16)
        for i in range(d2, n): m[i] += m[i-d2] * 0.09

        mx = max((abs(v) for v in m), default=1) or 1
        return _buf([int(v/mx*0.66*32767) for v in m])

    # Percussion pattern helper
    def _pp(bar_kicks, bar_snares, bar_hats, bars=4):
        out = []
        for b in range(bars):
            ob = b * 4
            for k in bar_kicks:  out.append(('kick',  ob+k))
            for s in bar_snares: out.append(('snare', ob+s))
            for h in bar_hats:   out.append(('hat',   ob+h))
        return out

    # ── 7 Pemberton-style biome tracks ───────────────────────────────────────
    # KA = King Arthur style  |  SV = Spider-Verse style

    # 0 – Jungle · SV · Dm7 · 124 BPM · hip-hop + orchestra
    #     Tribal percussion, driving syncopation, fierce brass motif
    def _music_0():
        # Spider-Verse: hkick+clap hip-hop groove, Dm7 jazz chords, punchy brass
        perc = (_pp([0,2],[],[0,.5,1,1.5,2,2.5,3,3.5]) +
                [(t,'hkick') for t in [0,2,4,6,8,10,12,14]] +
                [(t,'clap')  for t in [1,3,5,7,9,11,13,15]] +
                [('crash',0),('crash',8)])
        perc = [('hkick',b*4+k) for b in range(4) for k in [0,2]] + \
               [('clap', b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',  b*4+k*.5) for b in range(4) for k in range(8)] + \
               [('crash',0),('crash',8)]
        ost  = [(146.8, b*4, 4) for b in range(4)]
        mel  = [(440,0,1),(523.3,1,.5),(440,1.5,.5),(349.2,2,2),
                (392,4,.5),(440,4.5,.5),(523.3,5,1),(587.3,6,2),
                (523.3,8,1),(440,9,1),(392,10,.5),(349.2,10.5,.5),(293.7,11,1),
                (349.2,12,.5),(392,12.5,.5),(440,13,1),(523.3,14,.5),(440,14.5,.5),(349.2,15,1)]
        return _cin(124,[73.4,98.0,116.5,110],
                    [[146.8,174.6,220,261.6],[196,233.1,293.7,349.2],
                     [116.5,146.8,174.6,220],[110,138.6,164.8,220]],
                    perc, mel, ost, mamp=0.22)

    # 1 – Mountain · KA "A New World" · Dm · 140 BPM · relentless industrial march
    def _music_1():
        perc = [('kick',  b*4+k) for b in range(4) for k in [0,.5,2,3]] + \
               [('metal', b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',   b*4+k*.5) for b in range(4) for k in range(8)] + \
               [('crash',0),('crash',8)]
        ost  = [(146.8, b*4, 4) for b in range(4)]
        mel  = [(293.7,0,1),(349.2,1,1),(440,2,2),
                (523.3,4,.5),(440,4.5,.5),(349.2,5,1),(293.7,6,2),
                (440,8,1),(523.3,9,1),(587.3,10,2),
                (523.3,12,.5),(440,12.5,.5),(349.2,13,1),(293.7,14,1),(220,15,1)]
        return _cin(140,[73.4,65.4,58.3,65.4],
                    [[146.8,174.6,220],[130.8,164.8,196],
                     [116.5,146.8,174.6],[130.8,164.8,196]],
                    perc, mel, ost)

    # 2 – Desert · KA exotic · Am · 104 BPM · half-time industrial tension
    def _music_2():
        perc = [('kick',  b*4+k) for b in range(4) for k in [0,3]] + \
               [('metal', b*4+k) for b in range(4) for k in [2]] + \
               [('hat',   b*4+k) for b in range(4) for k in [0,1,2,3]]
        ost  = [(220, b*4, 4) for b in range(4)]
        mel  = [(440,0,1),(466.2,1,.5),(440,1.5,.5),(392,2,2),
                (349.2,4,1),(329.6,5,1),(293.7,6,2),
                (440,8,.5),(466.2,8.5,.5),(440,9,1),(392,10,1),(349.2,11,1),
                (329.6,12,2),(293.7,14,2)]
        return _cin(104,[110,87.3,73.4,82.4],
                    [[220,261.6,329.6],[233.1,293.7,349.2],
                     [146.8,174.6,220],[164.8,207.7,246.9]],
                    perc, mel, ost, mamp=0.20)

    # 3 – Volcano · KA "The Devil and the Huntsman" · Dm · 158 BPM · maximum power
    def _music_3():
        perc = [('kick',  b*4+k) for b in range(4) for k in [0,.5,1.5,2,2.5,3.5]] + \
               [('metal', b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',   b*4+k*.5) for b in range(4) for k in range(8)] + \
               [('crash',b*4) for b in range(4)]
        ost  = [(146.8, b*4+k*2, 2) for b in range(4) for k in range(2)]
        mel  = [(587.3,0,.5),(523.3,.5,.5),(440,1,.5),(523.3,1.5,.5),
                (587.3,2,.5),(659.3,2.5,.5),(698.5,3,1),
                (784,4,.5),(698.5,4.5,.5),(659.3,5,.5),(587.3,5.5,.5),
                (523.3,6,.5),(440,6.5,.5),(369.9,7,1),
                (440,8,1),(523.3,9,1),(659.3,10,1),(698.5,11,1),
                (784,12,.5),(698.5,12.5,.5),(659.3,13,.5),(587.3,13.5,.5),(440,14,2)]
        return _cin(158,[73.4,65.4,58.3,65.4],
                    [[146.8,174.6,220],[130.8,164.8,196],
                     [116.5,146.8,174.6],[130.8,164.8,196]],
                    perc, mel, ost)

    # 4 – Swamp · SV dark · Cm · 92 BPM · lo-fi hip-hop dread
    def _music_4():
        perc = [('hkick', b*4+k) for b in range(4) for k in [0,2.5]] + \
               [('clap',  b*4+k) for b in range(4) for k in [2]] + \
               [('metal', b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',   b*4+k) for b in range(4) for k in [0,1,2,3]]
        ost  = [(130.8, b*4, 4) for b in range(4)]
        mel  = [(523.3,0,2),(466.2,2,1),(415.3,3,1),
                (392,4,2),(349.2,6,2),
                (523.3,8,1),(493.9,9,1),(466.2,10,2),
                (440,12,1),(415.3,13,1),(392,14,1),(261.6,15,1)]
        return _cin(92,[65.4,87.3,103.8,116.5],
                    [[130.8,155.6,196],[174.6,207.7,261.6],
                     [207.7,261.6,311.1],[233.1,293.7,349.2]],
                    perc, mel, ost, mamp=0.20)

    # 5 – Arctic · SV "What's Up Danger" · Em · 130 BPM · hip-hop urgency
    def _music_5():
        perc = [('hkick', b*4+k) for b in range(4) for k in [0,1.5,2]] + \
               [('clap',  b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',   b*4+k*.5) for b in range(4) for k in range(8)] + \
               [('crash',0),('crash',8)]
        ost  = [(164.8, b*4, 4) for b in range(4)]
        mel  = [(329.6,0,.5),(392,.5,.5),(493.9,1,1),(587.3,2,.5),(523.3,2.5,.5),(493.9,3,1),
                (659.3,4,1),(587.3,5,1),(523.3,6,.5),(493.9,6.5,.5),(392,7,1),
                (493.9,8,.5),(587.3,8.5,.5),(659.3,9,1),(784,10,1),(880,11,1),
                (784,12,.5),(659.3,12.5,.5),(587.3,13,.5),(493.9,13.5,.5),(329.6,14,2)]
        return _cin(130,[82.4,98.0,73.4,110],
                    [[164.8,196,246.9],[196,246.9,293.7],
                     [146.8,185,220],[220,277.2,329.6]],
                    perc, mel, ost)

    # 6 – Ruins · KA "King Arthur" finale · Am · 118 BPM · everything at once
    def _music_6():
        perc = [('kick',  b*4+k) for b in range(4) for k in [0,2]] + \
               [('hkick', b*4+k) for b in range(4) for k in [.5,2.5]] + \
               [('metal', b*4+k) for b in range(4) for k in [1,3]] + \
               [('hat',   b*4+k*.5) for b in range(4) for k in range(8)] + \
               [('crash', b*4) for b in range(4)]
        ost  = [(110, b*4, 4) for b in range(4)]
        mel  = [(220,0,1),(261.6,1,1),(329.6,2,1),(261.6,3,1),
                (349.2,4,1),(329.6,5,1),(261.6,6,2),
                (440,8,.5),(523.3,8.5,.5),(659.3,9,1),(523.3,10,1),(440,11,1),
                (523.3,12,.5),(587.3,12.5,.5),(659.3,13,1),(523.3,14,1),(440,15,1)]
        return _cin(118,[55.0,87.3,65.4,98.0],
                    [[110,130.8,164.8],[174.6,220,261.6],
                     [130.8,164.8,196],[196,246.9,293.7]],
                    perc, mel, ost, mamp=0.26)

    # ── Lobby / calm music loop ───────────────────────────────────────────────
    def _lobby_music():
        BPM   = 82
        BEAT  = 60 / BPM
        total = 16 * BEAT
        n     = int(_R * total)
        mix   = [0.0] * n

        def add(start_t, len_t, freq, amp, decay=3.0, wave='sine'):
            s = int(start_t * _R)
            e = min(n, s + int(len_t * _R))
            for i in range(s, e):
                t = (i - s) / _R
                env = amp * math.exp(-decay * t)
                mix[i] += env * math.sin(2*math.pi*freq*t)

        def bt(bar, beat): return (bar*4 + beat) * BEAT

        chords = [[261.6,329.6,392],[349.2,440,523.3],[196,261.6,329.6],[293.7,369.9,440]]
        for bar, freqs in enumerate(chords):
            for f in freqs:
                add(bt(bar,0), BEAT*3.8, f, .16, 1.0, 'sine')
                add(bt(bar,2), BEAT*1.8, f*.5, .10, 0.8, 'sine')

        # Simple bell melody
        mel = [(523.3,0,1),(659.3,.5,.5),(783.9,1,1),(659.3,2,.5),(523.3,2.5,.5),(440,3,1),
               (392,4,2),(523.3,6,.5),(659.3,6.5,.5),(783.9,7,1),
               (880,8,1),(783.9,9,.5),(659.3,9.5,.5),(523.3,10,2)]
        for freq, boff, bdur in mel:
            add(boff*BEAT, BEAT*bdur*.9, freq, .18, 5.0, 'sine')

        # Soft kick pulse
        for bar in range(4):
            for b in [0, 2]:
                s = int(bt(bar, b) * _R)
                for i in range(min(n-s, int(_R*.15))):
                    t = i / _R
                    mix[s+i] += .35 * math.exp(-t*22) * math.sin(2*math.pi*55*t)

        mx = max((abs(v) for v in mix), default=1) or 1
        return _buf([int(v/mx*.65*32767) for v in mix])

    SOUNDS.update({
        "jump":           _jump(),
        "shoot_pistol":   _pistol(),
        "shoot_blaster":  _blaster(),
        "shoot_rifle":    _rifle(),
        "shoot_shotgun":  _shotgun(),
        "throw_grenade":  _throw(),
        "explosion":      _explosion(),
        "player_hit":     _player_hit(),
        "enemy_hit":      _enemy_hit(),
        "enemy_death":    _enemy_death(),
        "pickup_weapon":  _pickup_weapon(),
        "pickup_item":    _pickup_item(),
        "pickup_health":  _pickup_health(),
        "portal_open":    _portal_open(),
        "coin":           _coin(),
        "game_over":      _game_over(),
        "level_complete": _level_complete(),
        "music_lobby": _lobby_music(),   # procedural lobby fallback
    })


def play_music(key, volume=0.45):
    """Play a biome or lobby music track from file, loop indefinitely."""
    if "lobby" in key:
        fname = "lobby.mp3"
    else:
        try:
            biome = int(key.split("_")[1]) % 7
        except (IndexError, ValueError):
            return
        fname = f"biome_{biome}.mp3"

    path = os.path.join(MUSIC_DIR, fname)
    # Try a fresh download if the file is missing or corrupt
    if not os.path.exists(path) or not _valid_mp3(path):
        _fetch_music()
    if os.path.exists(path) and _valid_mp3(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            return
        except Exception as e:
            print(f"[music] could not play {fname}: {e}")

    # Fallback: procedural lobby track for calm, silence for action
    if "lobby" in key:
        s = SOUNDS.get("music_lobby")
        if s:
            pygame.mixer.Channel(0).play(s, loops=-1)


def stop_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    try:
        pygame.mixer.Channel(0).stop()
    except Exception:
        pass


def play(key, volume=1.0):
    s = SOUNDS.get(key)
    if s:
        s.set_volume(volume)
        s.play()
