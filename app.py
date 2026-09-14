import streamlit as st
import pandas as pd
from database import (
    insert_song, insert_song_source, fetch_all_songs, 
    fetch_all_recordings, create_recording, link_song_to_recording
)
from storage import save_image

st.set_page_config(page_title="Song Archive", layout="wide")
st.title("🎵 Bengali & Sanskrit Song Manager")

tab_entry, tab_recordings, tab_browse_recs, tab_view = st.tabs([
    "➕ Add New Song/Track", 
    "➕ Add Recordings", 
    "👁️ 📻 Browse Recordings", 
    "👁️ 📚 Browse Archive of Songs"
])

with tab_entry:
    with st.form("song_entry_form", clear_on_submit=True):
        title = st.text_input("Song Title*", placeholder="e.g., অন্নপূর্ণার বন্দনা")
        description = st.text_area("General Song Description / Background", height=100)
        raw_text = st.text_area("Raw Lyrics Text", height=150)

        # New Sarega notes field
        sarega = st.text_area("Sarega Notes", height=100, placeholder="eg: s r g g g m g r g p p p d p p g g r")

        # File upload input for source manuscripts or recordings
        uploaded_files = st.file_uploader(
            "Upload Manuscript Scans / Scores / Audio Files", 
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "pdf", "mp3", "wav"]
        )

        col1, col2 = st.columns(2)
        with col1:
            poet = st.text_input("Poet / Author", placeholder="e.g., Bharatchandra Ray")
            primary_language = st.selectbox("Primary Language", ["Bengali", "Sanskrit", "Hindi", "Brajbhasha", "Other"])
            languages = st.multiselect("Languages Present", ["Bengali", "Sanskrit", "Hindi", "Brajbhasha", "Maithili"], default=[primary_language])
            dialect = st.text_input("Dialect / Style", placeholder="e.g., Brajabuli")
            is_uncertain = st.checkbox("Language classification is uncertain")
            lang_notes = st.text_area("Language Notes", height=70)

        with col2:
            rag = st.text_input("Rāga", placeholder="e.g., Bhairavi")
            tal = st.text_input("Tāl / Rhythm", placeholder="e.g., Tripodi / Teental")
            raw_notes = st.text_area("Raw Stanza / Entry Notes", height=70)

        st.markdown("---")
        st.subheader("Associated Recordings & Media")
        
        # Multi-select existing recordings
        existing_recs = fetch_all_recordings()
        rec_options = {f"{r['title']} ({r['media_type']})": r['recording_id'] for r in existing_recs}
        selected_rec_labels = st.multiselect("Select Existing Recordings", list(rec_options.keys()))

        submitted = st.form_submit_button("Save Song & Links")
        
        if submitted:
            if not title: # or not raw_text:
                st.error("Please provide at least a Title.")
            else:
                song_id = insert_song(
                    title, poet, primary_language, languages, dialect, 
                    is_uncertain, lang_notes, rag, tal, description, raw_text, raw_notes, sarega
                )
                
                # Save uploaded files to disk and DB
                if uploaded_files:
                    for file in uploaded_files:
                        saved_path = save_image(file, folder_prefix="sources")
                        insert_song_source(
                            song_id=song_id, 
                            file_path=saved_path, 
                            file_name=file.name, 
                            source_notes="Uploaded via Song Entry form"
                        )

                # Link selected recordings
                for label in selected_rec_labels:
                    rec_id = rec_options[label]
                    link_song_to_recording(song_id, rec_id)

                st.success(f"Saved '{title}' (ID: {song_id}) with {len(uploaded_files) if uploaded_files else 0} file(s)!")

with tab_recordings:
    st.subheader("Add a Reusable Recording (CD, Cassette, YouTube link, MP3)")
    with st.form("new_recording_form", clear_on_submit=True):
        rec_title = st.text_input("Recording Title*", placeholder="e.g., AIR Kolkata 1984 Master Tape")
        media_type = st.selectbox("Media Type", ["Cassette", "CD", "DVD", "YouTube Link", "MP3 File", "Other"])
        url_loc = st.text_input("URL or Physical Location", placeholder="e.g., https://youtu.be/... or Shelf B-4")
        year = st.number_input("Release / Recording Year", min_value=1800, max_value=2030, value=1980)
        rec_notes = st.text_area("Recording Notes")
        
        rec_submitted = st.form_submit_button("Save Recording to Catalog")
        if rec_submitted:
            if rec_title:
                rid = create_recording(rec_title, media_type, url_loc, year, rec_notes)
                st.success(f"Added recording '{rec_title}' (ID: {rid})!")
            else:
                st.error("Recording title is required.")

with tab_browse_recs:
    st.subheader("Cataloged Recordings & Audio Media")
    recordings = fetch_all_recordings()
    if recordings:
        rec_df = pd.DataFrame(recordings)
        
        all_rec_cols = list(rec_df.columns)
        default_rec_cols = ["recording_id", "title", "media_type", "url_or_location", "release_year", "notes"]
        selected_rec_cols = st.multiselect(
            "Select columns to display:", 
            all_rec_cols, 
            default=[c for c in default_rec_cols if c in all_rec_cols],
            key="rec_col_select"
        )
        
        if selected_rec_cols:
            st.dataframe(rec_df[selected_rec_cols], width="stretch")
        else:
            st.dataframe(rec_df, width="stretch")
    else:
        st.info("No recordings found in database yet.")

with tab_view:
    st.subheader("Archived Songs")
    songs = fetch_all_songs()
    if songs:
        df = pd.DataFrame(songs)
        
        all_columns = list(df.columns)
        default_cols = ["song_id", "title", "description", "raw_text", "created_at"]
        selected_cols = st.multiselect(
            "Select columns to display:", 
            all_columns, 
            default=[c for c in default_cols if c in all_columns],
            key="song_col_select"
        )
        
        if selected_cols:
            st.dataframe(
                df[selected_cols], 
                width="stretch",
                column_config={
                    "description": st.column_config.TextColumn("Description", width="large"),
                    "raw_text": st.column_config.TextColumn("Raw Text", width="large"),
                }
            )
        else:
            st.dataframe(df, width="stretch")