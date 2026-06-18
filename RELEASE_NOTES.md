# Release v0.3.2

This is the publication-oriented submission patch for the seven-benchmark MMALS-CAL synthesis.

## Headline

Fresh calibration restores coverage; it does not manufacture competence. On CORe50, using inferred context to select among valid regime calibrators reduces coverage from 0.9011 to 0.7255, a 17.6 percentage-point loss.

## Reproducibility

The release includes all seven filtered traces and the complete replay implementation. Original upstream MMALS archives are excluded because of size and are not required for reproduction; their filenames and checksums are registered for later Drive or archive linking.

## Reviewer-orientation paper update

The canonical article now contains a dedicated section titled **From the Initial Gap Analysis to MMALS-CAL v0.3.2: Reviewer Orientation**. It summarizes what components A-D looked like before CAL, what v0.3.2 implements offline, and what remains necessary for online deployment. It also makes explicit that context inference is not change detection, that LAC nonconformity requires labels, and that a future runtime design needs label-free early warning followed by delayed-label statistical confirmation.
