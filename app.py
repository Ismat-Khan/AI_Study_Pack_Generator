                    [],
                ),
                1,
            ):

                with st.expander(
                    f"Card {index}: {card.get('question', '')}"
                ):

                    st.write(
                        card.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## ❓ MCQs")

            for index, mcq in enumerate(
                final.get(
                    "mcqs",
                    [],
                ),
                1,
            ):

                st.markdown(
                    f"**{index}. {mcq.get('question', '')}**"
                )

                options = mcq.get("options", {})

if isinstance(options, dict):
    for key, value in options.items():
        st.write(f"**{key}.** {value}")

elif isinstance(options, list):
    for index, option in enumerate(options):
        letter = chr(65 + index)
        st.write(f"**{letter}.** {option}")

else:
    st.write(str(options))

                with st.expander("Show answer"):

                    st.success(
                        str(
                            mcq.get(
                                "answer",
                                "",
                            )
                        )
                    )

                    st.write(
                        mcq.get(
                            "explanation",
                            "",
                        )
                    )

            st.markdown("## ✍️ Short Questions")

            for item in final.get(
                "short_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## 📖 Long Questions")

            for item in final.get(
                "long_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## 💡 Study Tips")

            for tip in final.get(
                "study_tips",
                [],
            ):
                st.write(f"• {tip}")

            st.download_button(
                "⬇️ Download Study Pack",
                data=json.dumps(
                    final,
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name="study_pack.json",
                mime="application/json",
            )

        else:
            st.info("Final refinement stage did not complete.")
