# Project Overview

## Purpose

Telegram-ggregator is a Telegram channel aggregator that automatically monitors configured source channels, filters new messages by keyword or regex rules, and republishes matching content to a target Telegram channel.

The service is intended to be delivered as a Python backend packaged as a Docker image.

## Primary Workflow

The target MVP workflow is:

1. Connect to Telegram using a user session.
2. Listen for new messages from configured source channels.
3. Evaluate each message against include and exclude filter rules.
4. Republish matching content to the configured target channel.
5. Prevent duplicate reposts across restarts.

## System Actors

- Service operator: configures sources, filters, runtime environment, and deployment.
- Telegram user session: grants read access to subscribed source channels through MTProto.
- Target channel subscribers: consume the aggregated posts.

## Current Repository State

- The repository currently contains an initial Python scaffold and container setup.
- The documented MVP below describes the intended target behavior, not a claim that the full feature set is already implemented.
- Where the current repository shape differs from the target specification, the specification remains the source of truth for product intent.
