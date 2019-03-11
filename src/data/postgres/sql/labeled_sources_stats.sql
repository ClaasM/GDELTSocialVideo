SELECT (SELECT Count(1) AS total FROM labeled_sources),
(SELECT Count(1) AS youtube FROM labeled_sources WHERE labeled_sources.youtube_relevant <> -1),
(SELECT Count(1) AS youtube_relevant FROM labeled_sources WHERE labeled_sources.youtube_relevant = 1),
(SELECT Count(1) AS twitter FROM labeled_sources WHERE labeled_sources.twitter_relevant <> -1),
(SELECT Count(1) AS twitter_relevant FROM labeled_sources WHERE labeled_sources.twitter_relevant = 1),
(SELECT Count(1) AS facebook FROM labeled_sources WHERE labeled_sources.facebook_relevant <> -1),
(SELECT Count(1) AS facebook_relevant FROM labeled_sources WHERE labeled_sources.facebook_relevant = 1);
