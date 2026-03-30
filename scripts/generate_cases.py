import json
from pathlib import Path


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    scenarios_dir = root / "scenarios"

    easy_drops = [
        "Library", "SAC", "FD2", "Shiv_Ganga", "IPC", "NAB", "Meera", "Sky_Lab", "Krishna", "LTC",
    ]
    medium_main_drops = [
        "Library", "FD2", "SAC", "NAB", "Meera", "Sky_Lab", "Krishna", "LTC", "Budh", "Shankar",
    ]
    medium_pickups = [
        "UCO_Bank", "IC", "CVR", "VFAST", "NAB", "Shiv_Ganga", "Library", "Main_Audi", "FD1", "Old_Workshop",
    ]
    medium_drop2 = [
        "Shiv_Ganga", "Meera", "Sky_Lab", "Birla_Museum", "IPC", "Saraswati_Mandir", "Ram", "Budh", "ANC", "Gym_Grounds",
    ]
    hard_main_drops = [
        ("Library", "SAC", "Sky_Lab"),
        ("FD2", "NAB", "Meera"),
        ("IPC", "Krishna", "LTC"),
        ("Shiv_Ganga", "Budh", "Ram"),
        ("Birla_Museum", "Sky_Lawns", "Saraswati_Mandir"),
        ("Gandhi", "Shankar", "Vyas"),
        ("FD1", "FD3", "Main_Audi"),
        ("IC", "SR", "ANC"),
        ("Gym_Grounds", "Akshay", "Bhagirath"),
        ("Old_Workshop", "New_Workshop", "Alumni_Home"),
    ]
    hard_pickups = [
        ("UCO_Bank", "Shiv_Ganga"),
        ("IC", "Meera"),
        ("CVR", "IPC"),
        ("VFAST", "NAB"),
        ("FD1", "SAC"),
        ("Old_Workshop", "Krishna"),
        ("Main_Audi", "Library"),
        ("SR", "Ram"),
        ("ANC", "Budh"),
        ("Gym_Grounds", "FD3"),
    ]

    for index in range(10):
        n = index + 1

        easy = {
            "name": f"easy_{n:02d}",
            "description": f"Easy case {n:02d}: two deliveries from Main Gate.",
            "start_node": "Main_Gate",
            "capacity": 2,
            "requests": [
                {"id": "r1", "pickup": "Main_Gate", "drop": easy_drops[index]},
                {"id": "r2", "pickup": "Main_Gate", "drop": easy_drops[(index + 3) % len(easy_drops)]},
            ],
        }

        medium = {
            "name": f"medium_{n:02d}",
            "description": f"Medium case {n:02d}: mixed gate and in-campus pickups.",
            "start_node": "Main_Gate",
            "capacity": 2,
            "requests": [
                {"id": "r1", "pickup": "Main_Gate", "drop": medium_main_drops[index]},
                {"id": "r2", "pickup": "Main_Gate", "drop": medium_main_drops[(index + 4) % len(medium_main_drops)]},
                {"id": "r3", "pickup": medium_pickups[index], "drop": medium_drop2[index]},
            ],
        }

        h1, h2, h3 = hard_main_drops[index]
        hp, hd = hard_pickups[index]
        hard = {
            "name": f"hard_{n:02d}",
            "description": f"Hard case {n:02d}: five requests across multiple zones.",
            "start_node": "Main_Gate",
            "capacity": 2,
            "requests": [
                {"id": "r1", "pickup": "Main_Gate", "drop": h1},
                {"id": "r2", "pickup": "Main_Gate", "drop": h2},
                {"id": "r3", "pickup": "Main_Gate", "drop": h3},
                {"id": "r4", "pickup": hp, "drop": hd},
                {
                    "id": "r5",
                    "pickup": medium_pickups[(index + 2) % len(medium_pickups)],
                    "drop": medium_drop2[(index + 5) % len(medium_drop2)],
                },
            ],
        }

        write_json(scenarios_dir / f"easy_{n:02d}.json", easy)
        write_json(scenarios_dir / f"medium_{n:02d}.json", medium)
        write_json(scenarios_dir / f"hard_{n:02d}.json", hard)

    print("generated 30")


if __name__ == "__main__":
    main()
