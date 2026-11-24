# Matrix rear plate - revision 2

This revision follows the marked rear-view sketch: four highlighted midpoint screws retain the plate; all four factory corner inserts stay exposed for magnetic standoffs. The controller is above/right of center, with its right PCB edge nominally 23 mm from the right inner plastic frame edge. The lever block is below/left of center. There are no PCB fingers, edge clamps, magnetic towers, or printed enclosures over the corner inserts.

## Print files

- `rear-plate-v2.stl`: the full plate, 191.8 x 191.8 mm, 3.2 mm plate thickness and 8 mm overall height at the six direct mounting posts.
- `m2-5-nut-trap-fit-test.stl`: 36 x 25 mm sample of the captive-nut pockets and screw bores. Print this first.
- `electronics-fit-check-v2.stl`: 95 x 95 mm footprint check containing the production six-post pattern and underside connector relief. The lever block may overhang its edge; it is a test coupon, not the final plate.

Files beginning `reference-` are assembly references only. Do not print them as mounting parts. The Blender file has a collection named `PRINT - rear plate only`; other collections contain reference electronics, fasteners, cable routes and dimensions.

## Hardware

- Four M3 x 6 mm countersunk screws for the panel's four midpoint inserts. The drawing calls out M3 x 5 inserts in the panel. Check engagement with the real frame before tightening; longer screws may bottom out.
- Four M2.5 x 8 mm screws for the controller's existing 2.5 mm holes. PCB mounting pitch is 40.64 x 19.685 mm, extracted from Adafruit's PCB source.
- Two M2.5 screws plus washers for the lever block's approximately 3 mm bores. M2.5 leaves about 0.5 mm diametral clearance in those bores. The modeled hole spacing is 19 mm.
- Six standard M2.5 hex nuts, nominally 5 mm across flats and 2 mm thick. Printed pockets are 5.25 mm across flats and 2.3 mm high. They load from the side via shallow loading wells and resist rotation.
- For the lever block, M2.5 x 8 screws suit mounting ears around 2 mm thick with thin washers. Thicker ears may need M2.5 x 10. Select the length after the fit check: fully engage the nut without bottoming against the 0.8 mm printed screw-tip floor or stressing the plastic ears.
- Cable ties for the supply entry and optional loose ribbon retention.

This revision uses captured M2.5 nuts rather than the originally proposed M3 heat-set inserts, following the updated screw sizes. No heat-set inserts are needed. Magnetic standoffs thread directly into the panel's four existing corner inserts; they do not attach to the printed plate.

## Orientation and cables

Orient the physical matrix to match the marked drawing, with the central frame rib horizontal, HUB75 input at upper left and matrix power at lower right. The source photographs were rotated 90 degrees clockwise for this view.

The horizontal lever block is turned end-for-end relative to the first proposal: its four-port side faces right towards both short power leads; its two-port side faces left for incoming supply. Keep the correct polarity and verify which ports are common on the actual connector. No conductors are connected or modified by this model.

Estimated centerline routes:

| Cable | Planned route | Supplied length | Nominal reserve |
| --- | ---: | ---: | ---: |
| Matrix power | 46.7 mm | 50.8 mm | 4.1 mm |
| Controller power | 69.8 mm | 100 mm | 30.2 mm |
| HUB75 ribbon | 220.4 mm | 254 mm | 33.6 mm |

The matrix pigtail is the limiting lead. These are schematic route lengths based on photo-derived connector locations, not a verified flexible harness simulation. Dry-fit that actual pigtail with its connector and wire takeoff before printing the complete plate. The ribbon route can be adjusted through the open space above and right of the board; do not force sharp creases or tighten ties onto it. In Blender, enable the cable reference collection in renders if desired.

## Printing and assembly

1. Print the nut-trap fit test and confirm your actual M2.5 nuts load and remain captured. If needed, change `m2_5_nut_across_flats` or pocket height in `rev2-parameters.json` and regenerate.
2. Print the electronics footprint check. Verify all four board holes, the 19 mm lever-ear pattern, underside female socket clearance, lever-ear seating, and both power leads. The lever body's 42 x 26 footprint comes from the similar reference image; 13.5 mm has been interpreted as its overall height. Its ear underside height was not supplied.
3. Print the full plate flat side down. Suggested starting settings: PETG, 0.2 mm layers, 4-5 walls, 5 top/bottom layers, 20-30% infill, supports off. The nut-pocket roofs are short bridges; inspect them after printing. Print at 100% scale.
4. Load the six M2.5 nuts. Retain them with the screws during handling if necessary. The printed posts are snugged gently; do not bend the controller or lever ears.
5. Attach the plate through the four midpoint M3 screws. Install the electronics, connect the existing harness, and check the capacitors and both HUB75 connectors through their relief openings.
6. Install your own magnetic standoffs in the exposed corner inserts. Nominal lever top is 21.5 mm above the panel mounting plane, with the schematic closed levers slightly higher; the connected IDC plug/cable may set the actual maximum. Check the real assembly before selecting standoff height. Around 25 mm is an initial clearance target, not a verified installed dimension.

## Dimensions that remain provisional

- The right inner frame edge is digitized at approximately 12.7 mm from the panel's outer edge. The 23 mm PCB inset is relative to that value. Measure the physical edge if the inset must be exact.
- Connector and capacitor positions are estimated from the supplied photos; their openings include clearance but the physical assembly has not been tested.
- Lever block body envelope, ear fore/aft position, ear elevation and mounting-hole diameter were not all measured on the actual part.
- No physical print, thermal test, magnetic load test, or connected-harness fit test has been performed.

The generated STLs are each one connected, watertight mesh with consistent winding. The corner clearance check confirms no printed geometry within a 25 mm radius of the four factory corner-hole centers. This is geometry validation, not physical fit validation.

## Source and regeneration

`rev2-parameters.json`, `build_mount_v2.py`, `csg.py` and `draw_layout_v2.py` are the editable source. The generated `.scad` files contain the same primitive CSG as the STL and can be opened in OpenSCAD. Their dimensions are baked; change the JSON and regenerate for parameter changes.

In the ZIP, these editable files are in `source/`. To rebuild, install `source/requirements.txt`, run `source/build_mount_v2.py`, then `source/draw_layout_v2.py`. Rebuilt files are written to `source/output/rev2/`. The Blender file is self-contained and does not require the source photographs or external STL files to open.

The Blender assembly is for inspection and layout review. Its official board mesh is embedded as reference, while printable mounting geometry is imported from the validated STL. Blender does not change the production mesh.

References:

- User-supplied `1484_P6_192X192mm-32x32pixel_2021 (1).pdf` for panel size and attachment centers.
- User-supplied photos and similar lever connector image, plus updated 19 mm pitch, 13.5 dimension, 100 mm controller lead and M2.5 fastener instructions.
- Adafruit MatrixPortal S3 PCB source: https://github.com/adafruit/Adafruit-MatrixPortal-S3-PCB
- Adafruit official board 3D reference: https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/5778%20Matrix%20Portal%20S3

Adafruit board designs are credited to Adafruit Industries and Limor Fried/Ladyada. The PCB source is licensed CC BY-SA 3.0; see the included Adafruit license. Original printable carrier geometry was generated for this request. The board reference is not part of any printable mounting STL.
