import { Deadlines } from '../types';
import { GAME_HOUR, GAME_MINUTE } from '../constants';

/**
 * Calculates the dates of the upcoming game days for the week.
 * If a game day has already passed for the current week, it schedules it for the following week.
 * @param gameDays - An array of target days of the week (0=Sun, 1=Mon, ..., 6=Sat).
 * @returns An array of Date objects for the upcoming game days.
 */
export const getUpcomingGameDates = (gameDays: number[]): Date[] => {
    const today = new Date();
    const upcomingDates: Date[] = [];

    gameDays.forEach(dayOfWeek => {
        const resultDate = new Date(today.getTime());
        const todayDay = today.getDay();
        
        let daysToAdd = (dayOfWeek + 7 - todayDay) % 7;
        
        // If it's today's game day, but we're past the game time, calculate for next week instead.
        if (daysToAdd === 0 && today.getHours() >= GAME_HOUR) {
            daysToAdd = 7;
        }
        
        resultDate.setDate(today.getDate() + daysToAdd);
        resultDate.setHours(GAME_HOUR, GAME_MINUTE, 0, 0);

        upcomingDates.push(resultDate);
    });

    return upcomingDates.sort((a, b) => a.getTime() - b.getTime());
};


/**
 * Calculates all relevant deadlines based on the game date.
 * @param gameDate - The Date of the badminton game.
 * @returns An object containing all deadline Date objects.
 */
export const calculateDeadlines = (gameDate: Date): Deadlines => {
    const gameDay = new Date(gameDate.getTime());

    const dayBefore = new Date(gameDay.getTime());
    dayBefore.setDate(gameDay.getDate() - 1);

    const registrationOpens = new Date(dayBefore.getTime());
    registrationOpens.setHours(8, 0, 0, 0); // Day before, 8:00 AM

    const guestRegistrationOpens = new Date(dayBefore.getTime());
    guestRegistrationOpens.setHours(20, 0, 0, 0); // Day before, 8:00 PM

    const registrationCloses = new Date(gameDay.getTime());
    registrationCloses.setHours(11, 0, 0, 0); // Game day, 11:00 AM

    const cancellationDeadline = new Date(gameDay.getTime());
    cancellationDeadline.setHours(12, 0, 0, 0); // Game day, 12:00 PM

    return {
        registrationOpens,
        registrationCloses,
        guestRegistrationOpens,
        cancellationDeadline,
    };
};

export const formatDate = (date: Date): string => {
    return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
    });
};