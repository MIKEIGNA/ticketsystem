import { useEffect, useState, useCallback } from 'react';
import { eventService } from '../services/events';

const POLL_INTERVAL_MS = 60_000; // 60 seconds

const STATUS_CONFIG = {
  live:       { label: '● LIVE',     className: 'bg-red-500 text-white animate-pulse' },
  finished:   { label: 'FT',         className: 'bg-gray-700 text-white' },
  halftime:   { label: 'HT',         className: 'bg-yellow-500 text-white' },
  postponed:  { label: 'POSTPONED',  className: 'bg-orange-500 text-white' },
  scheduled:  { label: 'UPCOMING',   className: 'bg-green-600 text-white' },
};

/**
 * MatchScore — displays live / final score for a football event.
 *
 * Props:
 *   slug        {string}  event slug
 *   matchData   {object}  event.match_data (used as initial state)
 *   startDatetime {string} ISO datetime of the match
 *   compact     {boolean} smaller layout for EventCard
 */
export default function MatchScore({ slug, matchData = {}, startDatetime, compact = false }) {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Determine if the match is close enough to warrant polling
  const shouldPoll = useCallback(() => {
    if (!startDatetime) return false;
    const start = new Date(startDatetime);
    const now = new Date();
    const diffMs = now - start;
    const diffHours = diffMs / (1000 * 60 * 60);
    // Poll if match started within the last 3 hours or starts within the next 10 minutes
    return diffHours >= -0.17 && diffHours <= 3;
  }, [startDatetime]);

  const fetchScore = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      const res = await eventService.getMatchScore(slug);
      setScore(res.data);
      setLastUpdated(new Date());
    } catch {
      // Silently fail — show stored data
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchScore();
    if (!shouldPoll()) return;
    const interval = setInterval(fetchScore, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchScore, shouldPoll]);

  // Merge: live data takes priority, fall back to matchData prop
  const home = score?.home_team || matchData?.home_team || '';
  const away = score?.away_team || matchData?.away_team || '';
  const homeLogo = score?.home_team_logo || matchData?.home_team_logo || '';
  const awayLogo = score?.away_team_logo || matchData?.away_team_logo || '';
  const homeScore = score?.home_score ?? matchData?.home_score ?? null;
  const awayScore = score?.away_score ?? matchData?.away_score ?? null;
  const matchStatus = score?.status || 'scheduled';
  const statusCfg = STATUS_CONFIG[matchStatus] || STATUS_CONFIG.scheduled;
  const hasScore = homeScore !== null && awayScore !== null;

  if (!home && !away) return null;

  if (compact) {
    // Compact version for EventCard overlay
    return hasScore ? (
      <div className="flex items-center gap-1 bg-black/70 text-white text-xs font-bold px-2 py-1 rounded-full">
        <span>{homeScore}</span>
        <span className="text-gray-400">-</span>
        <span>{awayScore}</span>
        {matchStatus === 'live' && (
          <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse ml-1" />
        )}
      </div>
    ) : null;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-100">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          Match Score
        </span>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${statusCfg.className}`}>
            {statusCfg.label}
          </span>
          {score?.progress && (
            <span className="text-xs text-gray-500">{score.progress}&apos;</span>
          )}
          <button
            onClick={fetchScore}
            disabled={loading}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-40"
            title="Refresh score"
          >
            {loading ? '⟳' : '↻'}
          </button>
        </div>
      </div>

      {/* Score display */}
      <div className="flex items-center justify-between px-6 py-5 gap-4">
        {/* Home team */}
        <div className="flex-1 flex flex-col items-center gap-2">
          {homeLogo ? (
            <img
              src={homeLogo}
              alt={home}
              className="w-14 h-14 object-contain drop-shadow"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">{home.charAt(0)}</span>
            </div>
          )}
          <span className="text-sm font-semibold text-gray-800 text-center leading-tight">
            {home}
          </span>
        </div>

        {/* Score / VS */}
        <div className="flex flex-col items-center gap-1 min-w-[80px]">
          {hasScore ? (
            <div className="flex items-center gap-2">
              <span className="text-4xl font-black text-gray-900">{homeScore}</span>
              <span className="text-2xl font-light text-gray-400">-</span>
              <span className="text-4xl font-black text-gray-900">{awayScore}</span>
            </div>
          ) : (
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-gray-600">VS</span>
            </div>
          )}
          {matchStatus === 'scheduled' && startDatetime && (
            <span className="text-xs text-gray-400">
              {new Date(startDatetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>

        {/* Away team */}
        <div className="flex-1 flex flex-col items-center gap-2">
          {awayLogo ? (
            <img
              src={awayLogo}
              alt={away}
              className="w-14 h-14 object-contain drop-shadow"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">{away.charAt(0)}</span>
            </div>
          )}
          <span className="text-sm font-semibold text-gray-800 text-center leading-tight">
            {away}
          </span>
        </div>
      </div>

      {/* Footer */}
      {lastUpdated && (
        <div className="px-4 py-1.5 bg-gray-50 border-t border-gray-100 text-center">
          <span className="text-xs text-gray-400">
            Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            {shouldPoll() && ' · auto-refreshes every 60s'}
          </span>
        </div>
      )}
    </div>
  );
}
