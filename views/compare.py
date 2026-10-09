"""Compare cities: does the next skill change with the city?"""
import altair as alt
import pandas  # noqa: F401
import streamlit as st

import findings

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
                 "Pick stability": row["confidence"],
                 "Flags": ", ".join(name for name, on in (("limited data", row["flags"]["limited_data"]),
                                                          ("few skills detected", row["flags"]["dictionary_warning"])) if on) or "none"})
frame = pandas.DataFrame(rows)
chart = alt.Chart(frame).mark_bar(color="#0f6b73").encode(
    x=alt.X("City:N", sort="-y"), y=alt.Y("Share matched:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
    tooltip=["City", "Matches", "Scored", "Fastest win", "Pick stability"])
st.altair_chart(chart, width="stretch")
st.caption("Bars show the share of scored listings the profile matches. Sample sizes differ a lot between cities; see the table.")
display = frame.assign(**{"Share matched": frame["Share matched"].map("{:.0%}".format)})
st.dataframe(display, hide_index=True, width="stretch")
reliable = [row for row in rows if row["Pick stability"] != "Uncertain" and "limited data" not in row["Flags"]]
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
weak = [row["City"] for row in rows if row["Pick stability"] == "Uncertain" or row["Scored"] < 12]
if weak:
    st.warning("Small or uncertain samples: " + ", ".join(weak) + ". Differences between cities may be noise.")

st.markdown("### Job-information gap")
gap = common.job_gap()
gap_frame = pandas.DataFrame([{"Role": row["role"], "City": row["city"], "Located in the city": row["in_city"],
                               "Visible listings": row["listings"], "Distinct employers": row["distinct_employers"],
                               "Pages fetched": row["pages_fetched"], "Snapshot": ", ".join(row["snapshot_dates"]),
                               "Most common other places": ", ".join(row["other_places"]) or "none"}
                              for row in gap["rows"]])
typical = round(sum(row["listings"] for row in gap["rows"]) / len(gap["rows"]))
st.write(f"Of the about {typical} listings Google Jobs returned for each query, how many were located in the named city.")
gap_chart = alt.Chart(gap_frame).mark_bar().encode(
    x=alt.X("City:N", sort=["Bengaluru", "Pune", "Jaipur", "Indore", "Dehradun"], title=None),
    xOffset="Role:N", y=alt.Y("Located in the city:Q", title="Listings located in the city"),
    color=alt.Color("Role:N", scale=alt.Scale(range=["#0f6b73", "#c76f00"])),
    tooltip=["Role", "City", "Located in the city", "Visible listings", "Most common other places"])
st.altair_chart(gap_chart, width="stretch")
st.write(findings.gap_sentence(gap))
st.caption("Listings visible through Google Jobs in this equal-query snapshot (the plain role name, no fresher or junior "
           "variants, three pages), not the number of jobs in a city. Every query filled all three pages, so the page limit "
           "sets the total. A listing counts as located in the city when its location text names the city; suburbs under "
           "other names do not count. Fewer local listings means less evidence to plan from, and NextSkill flags small "
           "samples instead of guessing. Saved markets use fresher and junior queries and an experience filter, so their counts "
           "are smaller.")
st.dataframe(gap_frame, hide_index=True, width="stretch")
