# P4.3 — One stationary world cup, two independently generated Spine rigs

The world object has exactly the **same coordinates** for both characters: initial cup center (270,195), final cup center (286,195). `studio.world.compile_world_motion` retains these positions even when character shoulders and arm lengths differ.

The action JSON is `examples/p4_coffee_motion.json`; it is authored once. Rig A: 90px+80px arm, shoulder (140,165). Rig B: 70px+65px arm, shoulder (175,185). Both characters approach the stationary mug handle; only rest wrist scales actor-locally, while the reach and place wrist targets are derived from the world object's stable socket. Carry waypoint is absolute and unscaled.

The prop has a LOCAL socket offset (-16,0). During carry it rotates smoothly from 0° to 25°, then returns to 0° during place. At each held frame its center is `actual Spine wrist + rotate(local socket, prop angle)`. The browser validates the world contact, not a procedural stand-in. Object orientation is a 2D screen-angle prototype (no physics, collisions or hand sprite grip animation).

**Explicit limits:** only single fixed-world object with one active actor per video and fixed camera. Multi-actor sharing one simultaneous cup, orientation-dependent hand pose, generic arbitrary skeleton chain, automatic rig detection, and voice/movie assembly are still open. The G-Labs live endpoint is intentionally not tested yet.
