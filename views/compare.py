"""Compare cities: does the next skill change with the city?"""
import altair as alt
import pandas  # noqa: F401
import streamlit as st

from scripts.build_results import summary
from views import common

common.language_bar()
st.header("Compare cities")
by_role: dict[str, list[dict]] = {}
for pair in common.pairs():
    by_role.setdefault(pair["role"], []).append(pair)
roles = [role for role, rows in by_role.items() if len(rows) >= 3]
if not roles:
    st.info("No role has three or more saved cities yet.")
    st.stop()
role = st.selectbox("Role", roles, index=roles.index("Data Analyst") if "Data Analyst" in roles else 0)
cities = by_role[role]
profile = common.current_profile(cities[0])
st.write(f"The same {role} fresher profile ({', '.join(profile['skills']) or 'no skills'}) checked against saved listings "
         f"in {len(cities)} cities.")
rows = []
for pair in cities:
    result = common.get_saved_result(pair["id"], profile["skills"], profile["threshold"], profile["core_share"],
                                     profile["experience"])
    row = summary(result)
    rows.append({"City": pair["city"], "Pages fetched": pair["pages"], "Snapshot": common.snapshot_text(pair["id"]),
                 "Eligible": row["eligible"],
                 "Scored": row["scored"], "Matches": row["matches"],
                 "Share matched": row["matches"] / row["scored"] if row["scored"] else 0.0,
                 "Fastest win": row["fastest_win"] or "Unavailable", "Biggest unlock": row["biggest_unlock"] or "Unavailable",
                 "Confidence": row["confidence"],
                 "Flags": ", ".join(name for name, on in (("limited data", row["flags"]["limited_data"]),
                                                          ("few skills detected", row["flags"]["dictionary_warning"])) if on) or "none"})
frame = pandas.DataFrame(rows)
chart = alt.Chart(frame).mark_bar().encode(
    x=alt.X("City:N", sort="-y"), y=alt.Y("Share matched:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
    tooltip=["City", "Matches", "Scored", "Fastest win", "Confidence"])
st.altair_chart(chart, width="stretch")
st.caption("Bars show the share of scored listings the profile matches. Sample sizes differ a lot between cities; see the table.")
display = frame.assign(**{"Share matched": frame["Share matched"].map("{:.0%}".format)})
st.dataframe(display, hide_index=True, width="stretch")
reliable = [row for row in rows if row["Confidence"] != "Uncertain" and "limited data" not in row["Flags"]]
picks = {row["Fastest win"] for row in reliable if row["Fastest win"] != "Unavailable"}
if not reliable:
    st.info("No reliable difference between these cities in this snapshot. Every city is Uncertain or has limited data, "
            "so a different fastest win in one city does not show that the best next skill differs.")
elif len(picks) == 1:
    st.success(f"Every city with a reliable pick agrees: the fastest win is {next(iter(picks))}.")
elif picks:
    st.info("The cities with a reliable pick do not agree. Fastest wins: " +
            "; ".join(f"{row['City']}: {row['Fastest win']}" for row in reliable) + ".")
if len({row["Pages fetched"] for row in rows}) > 1 or len({row["Snapshot"] for row in rows}) > 1:
    st.warning("These cities were not collected the same way: pages fetched or snapshot dates differ (see the table). "
               "Counts are not strictly like for like.")
weak = [row["City"] for row in rows if row["Confidence"] == "Uncertain" or row["Scored"] < 12]
if weak:
    st.warning("Small or uncertain samples: " + ", ".join(weak) + ". Differences between cities may be noise.")
