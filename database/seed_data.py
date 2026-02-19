"""
Seed the database with songs and movies across all 6 mood categories.
Run this script once to populate the database:
    python -m database.seed_data
"""

import os
import sys

# Allow running as module from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_utils import get_connection, init_db

# ── Song Data ────────────────────────────────────────────────────────────
SONGS = [
    # ── Happy ──
    ("Happy", "Pharrell Williams", "Pop", "happy",
     "https://www.youtube.com/watch?v=ZbZSe6N_BXs"),
    ("Walking on Sunshine", "Katrina & The Waves", "Pop", "happy",
     "https://www.youtube.com/watch?v=iPUmE-tne5U"),
    ("Uptown Funk", "Bruno Mars ft. Mark Ronson", "Funk/Pop", "happy",
     "https://www.youtube.com/watch?v=OPf0YbXqDm0"),
    ("Can't Stop the Feeling!", "Justin Timberlake", "Pop", "happy",
     "https://www.youtube.com/watch?v=ru0K8uYEZWw"),
    ("Good as Hell", "Lizzo", "Pop/R&B", "happy",
     "https://www.youtube.com/watch?v=SmbmeOgWsqE"),
    ("Shake It Off", "Taylor Swift", "Pop", "happy",
     "https://www.youtube.com/watch?v=nfWlot6h_JM"),
    ("I Gotta Feeling", "The Black Eyed Peas", "Pop", "happy",
     "https://www.youtube.com/watch?v=uSD4vsh1zDA"),
    ("Best Day of My Life", "American Authors", "Indie Pop", "happy",
     "https://www.youtube.com/watch?v=Y66j_BUCBMY"),
    ("On Top of the World", "Imagine Dragons", "Pop Rock", "happy",
     "https://www.youtube.com/watch?v=w5tWYmIOWGk"),
    ("Don't Stop Me Now", "Queen", "Rock", "happy",
     "https://www.youtube.com/watch?v=HgzGwKwLmgM"),

    # ── Sad ──
    ("Someone Like You", "Adele", "Pop/Soul", "sad",
     "https://www.youtube.com/watch?v=hLQl3WQQoQ0"),
    ("Fix You", "Coldplay", "Alternative Rock", "sad",
     "https://www.youtube.com/watch?v=k4V3Mo61fJM"),
    ("Say Something", "A Great Big World ft. Christina Aguilera", "Pop", "sad",
     "https://www.youtube.com/watch?v=-2U0Ivkn2Ds"),
    ("The Night We Met", "Lord Huron", "Indie Folk", "sad",
     "https://www.youtube.com/watch?v=KtlgYxa6BMU"),
    ("Hurt", "Johnny Cash", "Country", "sad",
     "https://www.youtube.com/watch?v=8AHCfZTRGiI"),
    ("Skinny Love", "Bon Iver", "Indie Folk", "sad",
     "https://www.youtube.com/watch?v=ssdgFoHLwnk"),
    ("Let Her Go", "Passenger", "Folk Pop", "sad",
     "https://www.youtube.com/watch?v=RBumgq5yVrA"),
    ("All I Want", "Kodaline", "Indie Rock", "sad",
     "https://www.youtube.com/watch?v=mtf7hC17IBM"),
    ("Tears in Heaven", "Eric Clapton", "Soft Rock", "sad",
     "https://www.youtube.com/watch?v=JxPj3GAYYZ0"),
    ("Mad World", "Gary Jules", "Alternative", "sad",
     "https://www.youtube.com/watch?v=4N3N1MlvVc4"),

    # ── Angry ──
    ("In the End", "Linkin Park", "Nu Metal", "angry",
     "https://www.youtube.com/watch?v=eVTXPUF4Oz4"),
    ("Killing in the Name", "Rage Against the Machine", "Rock", "angry",
     "https://www.youtube.com/watch?v=bWXazVhlyxQ"),
    ("Break Stuff", "Limp Bizkit", "Nu Metal", "angry",
     "https://www.youtube.com/watch?v=ZpUYjpKg9KY"),
    ("Numb", "Linkin Park", "Alternative Rock", "angry",
     "https://www.youtube.com/watch?v=kXYiU_JCYtU"),
    ("Bodies", "Drowning Pool", "Metal", "angry",
     "https://www.youtube.com/watch?v=04F4xlWSFh0"),
    ("Given Up", "Linkin Park", "Alternative Metal", "angry",
     "https://www.youtube.com/watch?v=0xyxtzD54rM"),
    ("Down with the Sickness", "Disturbed", "Nu Metal", "angry",
     "https://www.youtube.com/watch?v=09LTT0xwdfw"),
    ("Chop Suey!", "System of a Down", "Alternative Metal", "angry",
     "https://www.youtube.com/watch?v=CSvFpBOe8eY"),
    ("Last Resort", "Papa Roach", "Nu Metal", "angry",
     "https://www.youtube.com/watch?v=Hm7vnOC4hoY"),
    ("The Pretender", "Foo Fighters", "Rock", "angry",
     "https://www.youtube.com/watch?v=SBjQ9tuuTJQ"),

    # ── Neutral ──
    ("Viva la Vida", "Coldplay", "Alternative Rock", "neutral",
     "https://www.youtube.com/watch?v=dvgZkm1xWPE"),
    ("Clocks", "Coldplay", "Alternative Rock", "neutral",
     "https://www.youtube.com/watch?v=d020hcWA_Wg"),
    ("Sittin' on the Dock of the Bay", "Otis Redding", "Soul", "neutral",
     "https://www.youtube.com/watch?v=rTVjnBo96Ug"),
    ("Hotel California", "Eagles", "Rock", "neutral",
     "https://www.youtube.com/watch?v=BciS5krYL80"),
    ("Come Together", "The Beatles", "Rock", "neutral",
     "https://www.youtube.com/watch?v=45cYwDMibGo"),
    ("Breathe", "Pink Floyd", "Progressive Rock", "neutral",
     "https://www.youtube.com/watch?v=mrojrDCI02k"),
    ("Comfortably Numb", "Pink Floyd", "Progressive Rock", "neutral",
     "https://www.youtube.com/watch?v=_FrOQC-zEog"),
    ("Space Oddity", "David Bowie", "Art Rock", "neutral",
     "https://www.youtube.com/watch?v=iYYRH4apXDo"),
    ("The Sound of Silence", "Simon & Garfunkel", "Folk Rock", "neutral",
     "https://www.youtube.com/watch?v=4fWyzwo1xg0"),
    ("Bohemian Rhapsody", "Queen", "Rock", "neutral",
     "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"),

    # ── Excited ──
    ("Titanium", "David Guetta ft. Sia", "EDM", "excited",
     "https://www.youtube.com/watch?v=JRfuAukYTKg"),
    ("Levels", "Avicii", "EDM", "excited",
     "https://www.youtube.com/watch?v=_ovdm2yX4MA"),
    ("Stronger", "Kanye West", "Hip-Hop", "excited",
     "https://www.youtube.com/watch?v=PsO6ZnUZI0g"),
    ("Eye of the Tiger", "Survivor", "Rock", "excited",
     "https://www.youtube.com/watch?v=btPJPFnesV4"),
    ("We Will Rock You", "Queen", "Rock", "excited",
     "https://www.youtube.com/watch?v=-tJYN-eG1zk"),
    ("Lose Yourself", "Eminem", "Hip-Hop", "excited",
     "https://www.youtube.com/watch?v=_Yhyp-_hX2s"),
    ("Turn Down for What", "DJ Snake & Lil Jon", "EDM", "excited",
     "https://www.youtube.com/watch?v=HMUDVMiITOU"),
    ("Thunderstruck", "AC/DC", "Hard Rock", "excited",
     "https://www.youtube.com/watch?v=v2AC41dglnM"),
    ("Pump It", "The Black Eyed Peas", "Hip-Hop", "excited",
     "https://www.youtube.com/watch?v=ZaI2IlHwmgQ"),
    ("Enter Sandman", "Metallica", "Metal", "excited",
     "https://www.youtube.com/watch?v=CD-E-LDc384"),

    # ── Stressed ──
    ("Weightless", "Marconi Union", "Ambient", "stressed",
     "https://www.youtube.com/watch?v=UfcAVejslrU"),
    ("Clair de Lune", "Claude Debussy", "Classical", "stressed",
     "https://www.youtube.com/watch?v=CvFH_6DNRCY"),
    ("Breathe Me", "Sia", "Indie Pop", "stressed",
     "https://www.youtube.com/watch?v=SFGvmrJ5rjM"),
    ("River Flows in You", "Yiruma", "Classical", "stressed",
     "https://www.youtube.com/watch?v=7maJOI3QMu0"),
    ("Gymnopédie No.1", "Erik Satie", "Classical", "stressed",
     "https://www.youtube.com/watch?v=S-Xm7s9eGxU"),
    ("Sunset Lover", "Petit Biscuit", "Electronic/Chill", "stressed",
     "https://www.youtube.com/watch?v=wuCK-oiE3rM"),
    ("Re: Stacks", "Bon Iver", "Indie Folk", "stressed",
     "https://www.youtube.com/watch?v=GhDnyPsQBSA"),
    ("Bloom", "The Paper Kites", "Indie Folk", "stressed",
     "https://www.youtube.com/watch?v=w4XdnD5c334"),
    ("To Build a Home", "The Cinematic Orchestra", "Post-Rock", "stressed",
     "https://www.youtube.com/watch?v=oUFJJNQGwhk"),
    ("Everything's Not Lost", "Coldplay", "Alternative Rock", "stressed",
     "https://www.youtube.com/watch?v=frrFsIF6Gfo"),
]

# ── Movie Data ───────────────────────────────────────────────────────────
MOVIES = [
    # ── Happy ──
    ("The Pursuit of Happyness", "Drama/Biography", 2006, "happy",
     "Netflix", "https://www.netflix.com/title/70044605"),
    ("Forrest Gump", "Drama/Comedy", 1994, "happy",
     "Prime Video", "https://www.primevideo.com/detail/Forrest-Gump/0PIYQ4TED6Y6B6JNQQ37AHQW0K"),
    ("The Intern", "Comedy", 2015, "happy",
     "Netflix", "https://www.netflix.com/title/80047616"),
    ("Zootopia", "Animation/Comedy", 2016, "happy",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/zootopia/1260009992"),
    ("Paddington 2", "Comedy/Family", 2017, "happy",
     "Prime Video", "https://www.primevideo.com/detail/Paddington-2/0MZV8PRRKG2PW5UYYLJ1IM1MIR"),
    ("La La Land", "Musical/Romance", 2016, "happy",
     "Netflix", "https://www.netflix.com/title/80095365"),
    ("Inside Out", "Animation/Comedy", 2015, "happy",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/inside-out/1260009998"),
    ("The Secret Life of Walter Mitty", "Adventure/Comedy", 2013, "happy",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/walter-mitty/1260009150"),
    ("Up", "Animation/Adventure", 2009, "happy",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/up/1260009990"),
    ("Sing Street", "Musical/Drama", 2016, "happy",
     "Prime Video", "https://www.primevideo.com/detail/Sing-Street/0NMBNR0W93CL5PKGWNP9OTB05M"),

    # ── Sad ──
    ("The Fault in Our Stars", "Romance/Drama", 2014, "sad",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/the-fault-in-our-stars/1260009060"),
    ("A Star Is Born", "Drama/Music", 2018, "sad",
     "Prime Video", "https://www.primevideo.com/detail/A-Star-Is-Born/0PINLRQSJYA15JW6TS5KOFDXYE"),
    ("Schindler's List", "Drama/History", 1993, "sad",
     "Netflix", "https://www.netflix.com/title/60036359"),
    ("The Green Mile", "Drama/Fantasy", 1999, "sad",
     "Prime Video", "https://www.primevideo.com/detail/The-Green-Mile/0I8QUYB3HVXIJ3BHGVTM4ZXP6N"),
    ("Hachi: A Dog's Tale", "Drama/Family", 2009, "sad",
     "Prime Video", "https://www.primevideo.com/detail/Hachi-A-Dogs-Tale/0R8Y82VSXFZ0YX3CSYJ8GXRJJ4"),
    ("Marriage Story", "Drama/Romance", 2019, "sad",
     "Netflix", "https://www.netflix.com/title/80223779"),
    ("Manchester by the Sea", "Drama", 2016, "sad",
     "Prime Video", "https://www.primevideo.com/detail/Manchester-by-the-Sea/0R7AGKCVW6F0R0PS21RA1QRQV9"),
    ("Blue Valentine", "Drama/Romance", 2010, "sad",
     "Prime Video", "https://www.primevideo.com/detail/Blue-Valentine/0J5TXMXPID8DW2H54JQ3N6DHLX"),
    ("Grave of the Fireflies", "Animation/Drama", 1988, "sad",
     "Prime Video", "https://www.primevideo.com/detail/Grave-of-the-Fireflies/0HXWY5XPGDXBRNRJVQ2L3FR2O4"),
    ("Eternal Sunshine of the Spotless Mind", "Drama/Romance", 2004, "sad",
     "Prime Video", "https://www.primevideo.com/detail/Eternal-Sunshine/0QQWKN1ZRD2U89YCXKCV95BF5P"),

    # ── Angry ──
    ("John Wick", "Action/Thriller", 2014, "angry",
     "Prime Video", "https://www.primevideo.com/detail/John-Wick/0N2MIGZ1PXYCFQ7H34YI2R04XV"),
    ("Mad Max: Fury Road", "Action/Adventure", 2015, "angry",
     "Prime Video", "https://www.primevideo.com/detail/Mad-Max-Fury-Road/0PINLRQSJY4EX3NB8R13MZ8T8I"),
    ("Fight Club", "Drama/Thriller", 1999, "angry",
     "Prime Video", "https://www.primevideo.com/detail/Fight-Club/0L6DGKK8SYYGRHVWVLJ8DSGQIV"),
    ("Kill Bill: Vol. 1", "Action/Thriller", 2003, "angry",
     "Netflix", "https://www.netflix.com/title/60031236"),
    ("The Dark Knight", "Action/Drama", 2008, "angry",
     "Prime Video", "https://www.primevideo.com/detail/The-Dark-Knight/0SMBDWQ69CH77HWGMPCN2IM0ZM"),
    ("Gladiator", "Action/Drama", 2000, "angry",
     "Prime Video", "https://www.primevideo.com/detail/Gladiator/0T8443NJDRABRB5M37JXSH6QDM"),
    ("V for Vendetta", "Action/Thriller", 2005, "angry",
     "Netflix", "https://www.netflix.com/title/70039175"),
    ("300", "Action/Fantasy", 2006, "angry",
     "Prime Video", "https://www.primevideo.com/detail/300/0JPT36TXQMNFWFUOAG0X3HMI5V"),
    ("Django Unchained", "Western/Drama", 2012, "angry",
     "Netflix", "https://www.netflix.com/title/70230640"),
    ("Oldboy", "Thriller/Mystery", 2003, "angry",
     "Prime Video", "https://www.primevideo.com/detail/Oldboy/0MHXB10NUZPG4KKGX6P1IX4EPT"),

    # ── Neutral ──
    ("Inception", "Sci-Fi/Thriller", 2010, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/Inception/0PINLRQSJY7FKN6KSMQTMHQAFV"),
    ("The Grand Budapest Hotel", "Comedy/Drama", 2014, "neutral",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/the-grand-budapest-hotel/1260026103"),
    ("Interstellar", "Sci-Fi/Drama", 2014, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/Interstellar/0RF1RGHF0BQ7V0X8YGDCAH8JYT"),
    ("The Truman Show", "Comedy/Drama", 1998, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/The-Truman-Show/0N7UHMNTIJ7DSPGV2D3IPRJ2XJ"),
    ("Life of Pi", "Adventure/Drama", 2012, "neutral",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/life-of-pi/1260009103"),
    ("The Social Network", "Drama/Biography", 2010, "neutral",
     "Netflix", "https://www.netflix.com/title/70132721"),
    ("Her", "Drama/Romance", 2013, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/Her/0SNMYB1GNLP3FXSMVZUOPBWVMF"),
    ("Amélie", "Comedy/Romance", 2001, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/Amelie/0FLQ84E7SQZRBKB2P8KK1JY92T"),
    ("Lost in Translation", "Drama/Comedy", 2003, "neutral",
     "Prime Video", "https://www.primevideo.com/detail/Lost-in-Translation/0NQRMJFKH6CU2W2B1NV6N3F0F5"),
    ("Spirited Away", "Animation/Fantasy", 2001, "neutral",
     "Netflix", "https://www.netflix.com/title/60023642"),

    # ── Excited ──
    ("Avengers: Endgame", "Action/Sci-Fi", 2019, "excited",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/avengers-endgame/1260022800"),
    ("Top Gun: Maverick", "Action/Drama", 2022, "excited",
     "Prime Video", "https://www.primevideo.com/detail/Top-Gun-Maverick/0P9THGVLHH0D8JR36H6A9G8GYC"),
    ("Spider-Man: Into the Spider-Verse", "Animation/Action", 2018, "excited",
     "Netflix", "https://www.netflix.com/title/81002747"),
    ("Baby Driver", "Action/Music", 2017, "excited",
     "Netflix", "https://www.netflix.com/title/80142090"),
    ("Guardians of the Galaxy", "Action/Comedy", 2014, "excited",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/guardians-of-the-galaxy/1260009107"),
    ("Mission: Impossible - Fallout", "Action/Thriller", 2018, "excited",
     "Prime Video", "https://www.primevideo.com/detail/Mission-Impossible-Fallout/0QK2CGZOPQKC5DL13V7DHOFQLA"),
    ("The Matrix", "Sci-Fi/Action", 1999, "excited",
     "Prime Video", "https://www.primevideo.com/detail/The-Matrix/0K8TPJR2FD3GW7FPXLG7R0CLZP"),
    ("Ready Player One", "Sci-Fi/Adventure", 2018, "excited",
     "Prime Video", "https://www.primevideo.com/detail/Ready-Player-One/0QLVKQFX5HQB34V3J9HKKNTZR6"),
    ("Black Panther", "Action/Sci-Fi", 2018, "excited",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/black-panther/1260015803"),
    ("Jurassic World", "Action/Sci-Fi", 2015, "excited",
     "Prime Video", "https://www.primevideo.com/detail/Jurassic-World/0K2JRJ27KCXKJH94AI3P3XWPQQ"),

    # ── Stressed ──
    ("Soul", "Animation/Comedy", 2020, "stressed",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/soul/1260035131"),
    ("The Secret Garden", "Drama/Family", 2020, "stressed",
     "Prime Video", "https://www.primevideo.com/detail/The-Secret-Garden/0LDR4MZWG1M97TXYXVH48SBF9L"),
    ("My Neighbor Totoro", "Animation/Fantasy", 1988, "stressed",
     "Netflix", "https://www.netflix.com/title/60032294"),
    ("Midnight in Paris", "Comedy/Fantasy", 2011, "stressed",
     "Prime Video", "https://www.primevideo.com/detail/Midnight-in-Paris/0OQWV5F0DR79IJ2TXVKWG5GJPD"),
    ("The Hundred-Foot Journey", "Drama/Comedy", 2014, "stressed",
     "Disney+ Hotstar", "https://www.hotstar.com/in/movies/the-hundred-foot-journey/1260009113"),
    ("Chef", "Comedy/Drama", 2014, "stressed",
     "Netflix", "https://www.netflix.com/title/70297087"),
    ("Eat Pray Love", "Drama/Romance", 2010, "stressed",
     "Netflix", "https://www.netflix.com/title/70130775"),
    ("About Time", "Comedy/Romance", 2013, "stressed",
     "Netflix", "https://www.netflix.com/title/70261674"),
    ("The Way", "Adventure/Drama", 2010, "stressed",
     "Prime Video", "https://www.primevideo.com/detail/The-Way/0F2GKNN2M70F0B6RBZS1C2I9AB"),
    ("Piku", "Comedy/Drama", 2015, "stressed",
     "Netflix", "https://www.netflix.com/title/80073455"),
]


def seed_database():
    """Initialize schema and populate with seed data."""
    init_db()
    conn = get_connection()

    # Check if data already exists
    count = conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    if count > 0:
        print("Database already seeded. Skipping.")
        conn.close()
        return

    # Insert songs
    conn.executemany(
        "INSERT INTO songs (title, artist, genre, mood_tag, youtube_url) "
        "VALUES (?, ?, ?, ?, ?)",
        SONGS,
    )

    # Insert movies
    conn.executemany(
        "INSERT INTO movies (title, genre, year, mood_tag, ott_platform, ott_url) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        MOVIES,
    )

    conn.commit()
    print(f"✅ Seeded {len(SONGS)} songs and {len(MOVIES)} movies.")
    conn.close()


if __name__ == "__main__":
    seed_database()
