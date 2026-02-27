from dataclasses import dataclass, field


@dataclass
class Location:
    name_ar: str
    name_en: str
    keywords: list[str] = field(default_factory=list)


CHECKPOINTS: list[Location] = [
    Location("قلنديا", "Qalandia", ["قلنديا", "قلنديه", "حاجز قلنديا"]),
    Location("حوارة", "Huwwara", ["حوارة", "حواره", "حاجز حوارة"]),
    Location("زعترة", "Za'tara", ["زعترة", "زعتره", "حاجز زعترة", "تبوح"]),
    Location(
        "الكونتينر",
        "Container",
        ["الكونتينر", "كونتينر", "الكنتنر", "حاجز الكونتينر"],
    ),
    Location("جبع", "Jaba'", ["جبع", "حاجز جبع"]),
    Location("عناب", "Anab", ["عناب", "حاجز عناب"]),
    Location("عطارة", "Atara", ["عطارة", "عطاره", "حاجز عطارة"]),
    Location("بيت فوريك", "Beit Furik", ["بيت فوريك", "حاجز بيت فوريك"]),
    Location("صرّة", "Surra", ["صرة", "صره", "حاجز صرة"]),
    Location("عين سينيا", "Ein Sinya", ["عين سينيا", "عين سينية"]),
]

ROADS: list[Location] = [
    Location("وادي النار", "Wadi al-Nar", ["وادي النار", "وادي نار"]),
    Location(
        "طريق المعرجات",
        "Al-Ma'arrajat",
        ["المعرجات", "معرجات", "طريق المعرجات"],
    ),
    Location(
        "عيون حرامية", "Uyun Haramiya", ["عيون حرامية", "عيون الحرامية"]
    ),
    Location("النبي صالح", "Nabi Saleh", ["النبي صالح", "نبي صالح"]),
    Location("وادي قانا", "Wadi Qana", ["وادي قانا"]),
]

ALL_LOCATIONS = CHECKPOINTS + ROADS


def find_locations_in_text(text: str) -> list[Location]:
    """Return all locations mentioned in a message text."""
    found = []
    for loc in ALL_LOCATIONS:
        for kw in loc.keywords:
            if kw in text:
                found.append(loc)
                break
    return found
