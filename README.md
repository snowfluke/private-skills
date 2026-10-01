# Private Skills

Media skills that adapt to the product they run in, and one client-specific review skill.

| Skill | Use it to |
| --- | --- |
| `pmt-tatanan-lead-review` | Review a Tatanan PR. It extends `lead-review` from [tech-lead-skills](https://github.com/snowfluke/tech-lead-skills). |
| `app-launch-video` | Build a 90 s to 3 min launch video for an app you have the source of, in a direction invented for that product. Needs the HyperFrames skills: `npx skills add heygen-com/hyperframes -g`. |
| `motion-reel` | Build a 15 to 45 s looping motion-graphics reel, in a direction invented for that product. Needs Remotion. |

Each film starts from its own `DIRECTION.json`. `scripts/direction.py check`
rejects a direction that is not traced to the product or that is too close to
an earlier film. After delivery, `direction.py record` adds the film to your
history (`~/.local/share/video-directions/history.jsonl`). The two video skills
share `music.py`, `direction.py` and three references; `./check.sh` fails when
the copies differ.

Link the skills into your skills directory with `./link.sh` (default: `~/.claude/skills`).
Before you push, run `./check.sh`. CI runs it on every push.
