package com.brightpassticket.ui.theme

import androidx.compose.ui.graphics.Color

// FKF League Colors
val FKFRed = Color(0xFFDC3232)
val FKFBlack = Color(0xFF000000)
val FKFGreen = Color(0xFF43A047)

// SportPesa Sponsor Colors
val SportPesaBlue = Color(0xFF0059B3)
val SportPesaWhite = Color(0xFFFFFFFF)

// Club Primary Colors
object ClubColors {
    // Gor Mahia - Green
    val GorMahiaPrimary = Color(0xFF008000)
    val GorMahiaSecondary = Color(0xFFFFFFFF)
    
    // AFC Leopards - Blue
    val AFCLeopardsPrimary = Color(0xFF0000FF)
    val AFCLeopardsSecondary = Color(0xFFFFFFFF)
    
    // Tusker FC - Yellow
    val TuskerPrimary = Color(0xFFFFFF00)
    val TuskerSecondary = Color(0xFF000000)
    
    // KCB FC - Green & Gold
    val KCBPrimary = Color(0xFF006837)
    val KCBSecondary = Color(0xFFFFD700)
    
    // Ulinzi Stars - Red
    val UlinziPrimary = Color(0xFFED1C24)
    val UlinziSecondary = Color(0xFFFFFFFF)
    
    // Bandari FC - Blue & Yellow
    val BandariPrimary = Color(0xFF004A99)
    val BandariSecondary = Color(0xFFFDB913)
    
    // Kenya Police - Red & Blue
    val KenyaPolicePrimary = Color(0xFFCE1126)
    val KenyaPoliceSecondary = Color(0xFF0033A0)
    
    // Shabana FC - Red
    val ShabanaPrimary = Color(0xFFFF0000)
    val ShabanaSecondary = Color(0xFFFFFFFF)
    
    // Posta Rangers - Red
    val PostaRangersPrimary = Color(0xFFE31E24)
    val PostaRangersSecondary = Color(0xFFFFFFFF)
    
    // Kariobangi Sharks - Green & Black
    val SharksPrimary = Color(0xFF43A047)
    val SharksSecondary = Color(0xFF000000)
    
    // Mathare United - Red & Black
    val MatharePrimary = Color(0xFFDC3232)
    val MathareSecondary = Color(0xFF000000)
    
    // Murang'a SEAL - Red
    val MurangaSealPrimary = Color(0xFFDC3232)
    val MurangaSealSecondary = Color(0xFFFFFFFF)
    
    // Kakamega Homeboyz - Blue
    val HomeboyzPrimary = Color(0xFF0059B3)
    val HomeboyzSecondary = Color(0xFFFFFFFF)
    
    // Sofapaka - Blue
    val SofapakaPrimary = Color(0xFF0059B3)
    val SofapakaSecondary = Color(0xFFFFFFFF)
    
    // Bidco United - Green
    val BidcoPrimary = Color(0xFF43A047)
    val BidcoSecondary = Color(0xFFFFFFFF)
    
    // Nairobi United - Blue
    val NairobiUnitedPrimary = Color(0xFF0059B3)
    val NairobiUnitedSecondary = Color(0xFFFFFFFF)
    
    // Mara Sugar - Green
    val MaraSugarPrimary = Color(0xFF43A047)
    val MaraSugarSecondary = Color(0xFFFFFFFF)
    
    // APS Bomet - Red
    val APSBometPrimary = Color(0xFFDC3232)
    val APSBometSecondary = Color(0xFFFFFFFF)
}

// Helper function to get club colors by name
fun getClubColors(clubName: String): Pair<Color, Color> {
    return when (clubName) {
        "Gor Mahia" -> ClubColors.GorMahiaPrimary to ClubColors.GorMahiaSecondary
        "AFC Leopards" -> ClubColors.AFCLeopardsPrimary to ClubColors.AFCLeopardsSecondary
        "Tusker FC" -> ClubColors.TuskerPrimary to ClubColors.TuskerSecondary
        "KCB FC" -> ClubColors.KCBPrimary to ClubColors.KCBSecondary
        "Ulinzi Stars" -> ClubColors.UlinziPrimary to ClubColors.UlinziSecondary
        "Bandari FC" -> ClubColors.BandariPrimary to ClubColors.BandariSecondary
        "Kenya Police FC" -> ClubColors.KenyaPolicePrimary to ClubColors.KenyaPoliceSecondary
        "Shabana FC" -> ClubColors.ShabanaPrimary to ClubColors.ShabanaSecondary
        "Posta Rangers" -> ClubColors.PostaRangersPrimary to ClubColors.PostaRangersSecondary
        "Kariobangi Sharks" -> ClubColors.SharksPrimary to ClubColors.SharksSecondary
        "Mathare United" -> ClubColors.MatharePrimary to ClubColors.MathareSecondary
        "Murang'a SEAL" -> ClubColors.MurangaSealPrimary to ClubColors.MurangaSealSecondary
        "Kakamega Homeboyz" -> ClubColors.HomeboyzPrimary to ClubColors.HomeboyzSecondary
        "Sofapaka FC" -> ClubColors.SofapakaPrimary to ClubColors.SofapakaSecondary
        "Bidco United" -> ClubColors.BidcoPrimary to ClubColors.BidcoSecondary
        "Nairobi United" -> ClubColors.NairobiUnitedPrimary to ClubColors.NairobiUnitedSecondary
        "Mara Sugar FC" -> ClubColors.MaraSugarPrimary to ClubColors.MaraSugarSecondary
        "APS Bomet" -> ClubColors.APSBometPrimary to ClubColors.APSBometSecondary
        else -> Color.Gray to Color.White
    }
}
