import requests
import pprint
import re
import streamlit as st

st.title("The Szmalcesony")
st.set_page_config(layout='wide')


def parse_infobox(wikitext):
    fields = {}

    for line in wikitext.splitlines():
        match = re.match(r"^\|\s*([^=]+?)\s*=\s*(.*)$", line)

        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            fields[key] = value

    return fields

def get_wikia_data(item):
    url = "https://tibia.fandom.com/api.php"
    result = {}

    params = {
        "action": "query",
        "prop": "revisions",
        "titles": item,
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }

    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "TibiaDataExplorer/1.0 (personal project)"},
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()
    print(data)
    

    for page_id in data["query"]["pages"]:
        page = data["query"]["pages"][page_id]
        title = page["title"]
        wikitext = page["revisions"][0]["slots"]["main"]["*"]

        creature = parse_infobox(wikitext)

        name = creature.get("name")
        hp = creature.get("hp")
        holy =  creature.get("holyDmgMod")
        physical = creature.get("physicalDmgMod")
        energy = creature.get("energyDmgMod")
        earth =  creature.get("earthDmgMod")
        ice =  creature.get("iceDmgMod")
        death = creature.get("deathDmgMod")
        fire =  creature.get("fireDmgMod")

        result[name] = {
            "Holy damage modifier": holy,
            "Physical damage modifier": physical,
            "Energy damage modifier": energy,
            "Earth damage modifier": earth,
            "Ice damage modifier": ice,
            "Death damage modifier": death, 
            "Fire damage modifier": fire,
            
        }
    return result

def get_color_of_item(resist_number):
    resist_number = int(resist_number.replace("%", "").replace("?", "").replace(">", "").replace("<", ""))
    if resist_number >= 90:
        return f":green[{resist_number} %]"
    elif resist_number < 90 and resist_number >= 75:
        return f":yellow[{resist_number} %]"
    else:
        return f":red[{resist_number} %]"

@st.cache_data(ttl=3600)
def collect_all_monster_names():
    API_URL = "https://tibia.fandom.com/api.php"

    monster_names = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Bosses",
        "cmtype": "page",
        "cmlimit": "max",
        "format": "json",
    }

    while True:
        response = requests.get(
            API_URL,
            params=params,
            headers={"User-Agent": "TibiaMonsterSearch/1.0"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        monster_names.extend(
            page["title"]
            for page in data["query"]["categorymembers"]
        )

        continuation = data.get("continue")
        if not continuation:
            break

        params.update(continuation)

    print(f"Collected {len(monster_names)} page names")
    return monster_names

def search_monsters(query, monster_names):
    query = query.strip().casefold()

    if not query:
        return []

    return [
        name
        for name in monster_names
        if query in name.casefold()
    ]

@st.cache_data(ttl=3600)
def display_monster_data(selected_monster, extra_info=None):
    data = get_wikia_data([selected_monster])
    st.markdown(f"#### {selected_monster}")
    holy = data[selected_monster]["Holy damage modifier"]
    phys = data[selected_monster]["Physical damage modifier"]
    energy = data[selected_monster]["Energy damage modifier"]
    earth = data[selected_monster]["Earth damage modifier"]
    ice = data[selected_monster]["Ice damage modifier"]
    death = data[selected_monster]["Death damage modifier"]
    fire = data[selected_monster]["Fire damage modifier"]

    st.markdown(f"###### 🌟 Holy damage modifier: {get_color_of_item(holy)}")
    st.markdown(f"###### 🗡️ Physical damage modifier: {get_color_of_item(phys)}")
    st.markdown(f"###### ⚡ Energy damage modifier: {get_color_of_item(energy)}")
    st.markdown(f"###### 🌱 Earth damage modifier: {get_color_of_item(earth)}")
    st.markdown(f"###### ❄️ Ice damage modifier: {get_color_of_item(ice)}")
    st.markdown(f"###### 💀 Death damage modifier: {get_color_of_item(death)}")
    st.markdown(f"###### 🔥 Fire damage modifier: {get_color_of_item(fire)}")

    if extra_info:
        st.markdown(f"###### {extra_info}")

monster_names = collect_all_monster_names()

tab1, tab2 = st.tabs(["Bosses", "Items"])
with tab1: 
    col_1, col_temp,  col_2 = st.columns([3,1,3])

    with col_1:
        query = st.text_input("Search for a boss")

        if query:
            matches = search_monsters(query, monster_names)

            if matches:
                selected_monster = st.selectbox(
                    "Select a boss",
                    matches
                )
                display_monster_data(selected_monster)

            else:
                st.warning("No matching bosses found.")

    with col_2:
        with st.expander("Popular bosses", expanded=True):
            with st.expander("Grave Danger"):
                with st.expander("Earl Osam (Cormaya)"):
                    display_monster_data("Earl Osam")

                with st.expander("Count Vlarkorth (Edron)"):
                    display_monster_data("Count Vlarkorth")

                with st.expander("Sir Baeloc & Sir Nictros (Darashia)"):
                    display_monster_data("Sir Baeloc")
                    display_monster_data("Sir Nictros")

                with st.expander("Lord Azaram (Carlin)"):
                    display_monster_data("Lord Azaram")

                with st.expander("Duke Krule (Thais)"):
                    display_monster_data("Duke Krule")

            with st.expander("Gold Token (HoD)"):
                with st.expander("Rupture (Zao)"):
                    display_monster_data("Rupture")

                with st.expander("Realityquake (Svargrond)"):
                    display_monster_data("Foreshock")
                    display_monster_data("Aftershock")
                    display_monster_data("Realityquake")

                with st.expander("Anomaly (Darama)"):
                    display_monster_data("Anomaly")

                with st.expander("Outburst (Inner)"):
                    display_monster_data("Lord Azaram")

                with st.expander("Eradicator (Inner)"):
                    display_monster_data("Eradicator")


            
            with st.expander("Dragon Pack (Despor)"):
                with st.expander("Maliz"):
                    display_monster_data("Maliz")

                with st.expander("Vengar"):
                    display_monster_data("Vengar")

                with st.expander("Greedok"):
                    display_monster_data("Greedok")

                with st.expander("Crultor"):
                    display_monster_data("Crultor")

                with st.expander("Despor"):
                    display_monster_data("Despor")

                with st.expander("Bruton"):
                    display_monster_data("Bruton")

                with st.expander("Vilear"):
                    display_monster_data("Vilear")

with tab2:
    st.markdown("Strona w trakcie projektowania")