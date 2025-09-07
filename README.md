# DrawDesign - Pen/Paper to Landing Page

## Overview

DrawDesign is a tool that helps lower the barrier to entry for creating websites. We wanted to build it to esepcially help small business owners who aren't neccessarily technical to turn the ideas in their head into reality. We think this can also help designers for rapid prototyping by integrating into their existing component library. Designers still like visualizing their barebones ideas with pen and paper. This extends that by showing a live demo on the web.

## Running the Program

Just download our dependencies and run 'uv run unskew.py' in your terminal!

## Technical Highlights

- Unskewing through image processing - wanted to let designers work as quickly as possible by being able to draw their design out on pen and paper in front of them and then quickly turn their camera computer down to capture their work. We manage to unskew the image despite the computer tilt through linear algebra.
- Content extraction from initial image - we call OpenAI APIs to digest the initial sketch and identify the key components of the landing page so that it can spin up a website.
- Additional narration modality - we incorporate speech so that the designer can talk thought their thoughts while sketching and even if they miss something on paper, they can tell the software to add it verbally.
- Multiple iterations for editing - we know that prototyping is a multi-step process and that you don't always get it right the first time. Thus, we wanted to let the designer edit by red-lining their design on paper. We then weave these edits into the website. The designer can keep iterating until they feel satisfied with the outcome.

## Team

DrawDesign was developed by a team of AI engineers and product designers passionate about making design more accessible.
