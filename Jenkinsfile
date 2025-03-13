#!/usr/bin/env groovy
@Library('tailor-meta@0.1.25')_
tailorTestPipeline(
  // Name of job that generated this test definition.
  rosdistro_job: '/ci/rosdistro/release%2F25.0',
  // Distribution name
  rosdistro_name: 'ros2',
  // Release track to test branch against.
  release_track: '25.0',
  // Release label to pull test images from.
  release_label: '25.0-rc',
  // OS distributions to test.
  distributions: ['jammy'],
  // Version of tailor_meta to build against
  tailor_meta: '0.1.25',
  // Master or release branch associated with this track
  source_branch: 'release/25.0/ros2',
  // Docker registry where test image is stored
  docker_registry: 'https://084758475884.dkr.ecr.us-east-1.amazonaws.com/locus-tailor'
)