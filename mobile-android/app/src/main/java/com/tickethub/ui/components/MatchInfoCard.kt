package com.brightpassticket.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.brightpassticket.data.model.MatchData
import com.brightpassticket.ui.theme.*

@Composable
fun MatchInfoCard(
    matchData: MatchData,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header with badges
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Match Info",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    // FKF Badge
                    FKFBadge()
                    // SportPesa Badge
                    SportPesaBadge()
                    // Category Badge
                    CategoryBadge(matchData.category)
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Teams display
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Home Team
                TeamDisplay(
                    teamName = matchData.homeTeam,
                    logoUrl = matchData.homeTeamLogo,
                    primaryColor = matchData.homeTeamPrimaryColor?.let { Color(android.graphics.Color.parseColor(it)) } 
                        ?: Color.Gray,
                    isHome = true
                )
                
                // VS
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "VS",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                    )
                    Text(
                        text = matchData.category + " Cat",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
                
                // Away Team
                TeamDisplay(
                    teamName = matchData.awayTeam,
                    logoUrl = matchData.awayTeamLogo,
                    primaryColor = matchData.awayTeamPrimaryColor?.let { Color(android.graphics.Color.parseColor(it)) } 
                        ?: Color.Gray,
                    isHome = false
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Stadium info
            Text(
                text = "📍 ${matchData.stadium}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }
    }
}

@Composable
private fun TeamDisplay(
    teamName: String,
    logoUrl: String?,
    primaryColor: Color,
    isHome: Boolean
) {
    val homeColors = listOf(primaryColor, primaryColor.copy(alpha = 0.8f))
    val borderColor = primaryColor
    
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.width(100.dp)
    ) {
        // Logo with team color border
        Box(
            modifier = Modifier
                .size(72.dp)
                .clip(CircleShape)
                .background(Color.White)
                .border(3.dp, borderColor, CircleShape)
                .padding(4.dp),
            contentAlignment = Alignment.Center
        ) {
            if (!logoUrl.isNullOrEmpty()) {
                AsyncImage(
                    model = logoUrl,
                    contentDescription = teamName,
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(CircleShape),
                    contentScale = ContentScale.Fit
                )
            } else {
                // Fallback to first letter
                Text(
                    text = teamName.take(1).uppercase(),
                    style = MaterialTheme.typography.headlineLarge,
                    color = primaryColor,
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Team name
        Text(
            text = teamName,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            maxLines = 2
        )
        
        // Home/Away label
        Text(
            text = if (isHome) "Home" else "Away",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
        )
    }
}

@Composable
private fun FKFBadge() {
    val fkfGradient = Brush.horizontalGradient(
        colors = listOf(FKFRed, FKFBlack, FKFGreen)
    )
    
    Box(
        modifier = Modifier
            .background(fkfGradient, RoundedCornerShape(4.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = "FKF",
            color = Color.White,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun SportPesaBadge() {
    Box(
        modifier = Modifier
            .background(SportPesaBlue, RoundedCornerShape(4.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = "SportPesa",
            color = Color.White,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun CategoryBadge(category: String) {
    val (bgColor, textColor) = when (category) {
        "A" -> Color(0xFFFFD700) to Color.Black  // Gold
        "B" -> Color(0xFFC0C0C0) to Color.Black  // Silver
        "C" -> Color(0xFFCD7F32) to Color.White  // Bronze
        else -> MaterialTheme.colorScheme.surfaceVariant to MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Box(
        modifier = Modifier
            .background(bgColor, RoundedCornerShape(12.dp))
            .padding(horizontal = 12.dp, vertical = 4.dp)
    ) {
        Text(
            text = "$category Category",
            color = textColor,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
