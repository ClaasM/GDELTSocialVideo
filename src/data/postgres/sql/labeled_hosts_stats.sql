SELECT (SELECT Count(1) AS total FROM labeled_hosts),
(SELECT Count(1) AS youtube FROM labeled_hosts WHERE labeled_hosts.youtube_relevant <> -1),
(SELECT Count(1) AS youtube_relevant FROM labeled_hosts WHERE labeled_hosts.youtube_relevant = 1),
(SELECT Count(1) AS twitter FROM labeled_hosts WHERE labeled_hosts.twitter_relevant <> -1),
(SELECT Count(1) AS twitter_relevant FROM labeled_hosts WHERE labeled_hosts.twitter_relevant = 1),
(SELECT Count(1) AS facebook FROM labeled_hosts WHERE labeled_hosts.facebook_relevant <> -1),
(SELECT Count(1) AS facebook_relevant FROM labeled_hosts WHERE labeled_hosts.facebook_relevant = 1);
