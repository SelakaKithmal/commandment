// iTunes Search API
// Structures taken from Documentation, available at:
// https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/

export const ITUNES_SEARCH_URL: string = "https://itunes.apple.com/search";

export enum MediaType {
    movie = "movie",
    podcast = "podcast",
    music = "music",
    musicVideo = "musicVideo",
    audiobook = "audiobook",
    shortFilm = "shortFilm",
    tvShow = "tvShow",
    software = "software",
    ebook = "ebook",
    all = "all",
}

export enum EntityType {
    movieArtist = "movieArtist",
    movie = "movie",

    podcastAuthor = "podcastAuthor",
    podcast = "podcast",

    musicArtist = "musicArtist",
    musicTrack = "musicTrack",
    album = "album",
    musicVideo = "musicVideo",
    mix = "mix",
    song = "song",

    audiobookAuthor = "audiobookAuthor",
    audiobook = "audiobook",

    shortFilmArtist = "shortFilmArtist",
    shortFilm = "shortFilm",

    tvEpisode = "tvEpisode",
    tvSeason = "tvSeason",

    software = "software",
    iPadSoftware = "iPadSoftware",
    macSoftware = "macSoftware",

    ebook = "ebook",

    allArtist = "allArtist",
    allTrack = "allTrack",
}

export interface IMediaTypeEntityList {
    [propName: string]: string[];
}

export const MediaTypeEntities: IMediaTypeEntityList = {
    [MediaType.software]: [
        "software",
        "iPadSoftware",
        "macSoftware",
    ],
};

export enum MovieAttribute {
    actorTerm = "actorTerm",
    genreIndex = "genreIndex",
    artistTerm = "artistTerm",
    shortFilmTerm = "shortFilmTerm",
    producerTerm = "producerTerm",
    ratingTerm = "ratingTerm",
    directorTerm = "directorTerm",
    releaseYearTerm = "releaseYearTerm",
    featureFilmTerm = "featureFilmTerm",
    movieArtistTerm = "movieArtistTerm",
    movieTerm = "movieTerm",
    ratingIndex = "ratingIndex",
    descriptionTerm = "descriptionTerm",
}

export enum ArtworkIconSize {
    Sixty = "artworkUrl60",
    Hundred = "artworkUrl100",
    FiveTwelve = "artworkUrl512",
}

export interface IItunesSearchQuery {
    term: string;
    country: string;
    media?: MediaType;
    entity?: EntityType;
    attribute?: string;
    callback?: string;
    limit?: number;
    lang?: string;
    version?: number;
    explicit?: string;
}

export interface IiTunesSearchResult {
    resultCount: number;
    results: IiTunesSoftwareSearchResult[];
}

export enum IiTunesSoftwareKind {
    software = "software",
    macSoftware = "mac-software",
}

export interface IiTunesSoftwareSearchResult {
    isGameCenterEnabled: boolean;
    ipadScreenshotUrls: string[];
    screenshotUrls: string[];
    appletvScreenshotUrls: string[];
    artworkUrl60: string;
    artworkUrl512: string;
    artworkUrl100: string;
    artistViewUrl: string;
    advisories: string[];
    supportedDevices: string[];
    kind: IiTunesSoftwareKind;
    features: string[];
    trackCensoredName: string;
    languageCodesISO2A: string[];
    fileSizeBytes: number;
    sellerUrl: string;
    contentAdvisoryRating: string;
    trackViewUrl: string;
    trackContentRating: string;
    releaseNotes: string;
    formattedPrice: string;
    trackName: string;
    primaryGenreName: string;
    genreIds: string[];
    sellerName: string;
    releaseDate: string;  // eg 2016-11-04T19:34:13Z
    primaryGenreId: number;
    isVppDeviceBasedLicensingEnabled: boolean;
    currency: string;
    wrapperType: string;
    version: string;
    trackId: number;
    description: string;
    artistId: number;
    artistName: string;
    genres: string[];
    price: number;
    minimumOsVersion: string;
    bundleId: string;
    currentVersionReleaseDate: string;
    averageUserRating: number;
    userRatingCount: number;
}
